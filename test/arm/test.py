import os
import urllib
import time
from bs4 import BeautifulSoup

import undetected_chromedriver.v2 as uc
from xvfbwrapper import Xvfb

def get_translation(text):
    text = urllib.parse.quote(text)

    vdisplay = Xvfb(width=800, height=1280)
    vdisplay.start()

    options = uc.ChromeOptions()
#    options.add_argument(f'--no-first-run --no-service-autorun --password-store=basic')
#    options.add_argument(f'--disable-gpu')
    options.add_argument(f'--no-sandbox')
    options.add_argument(f'--disable-dev-shm-usage')

    driver = uc.Chrome(options=options, headless=False)

    translation = ''
    with driver:
        driver.get("https://translate.yandex.ru/?lang=en-ru&text=" + text)

        time.sleep(5)

        html = driver.page_source
        with open("html.html", "w") as f:
            f.write(html)
            print(html)

        if "Нам очень жаль, но запросы с вашего устройства похожи на автоматические" in html:
            raise Exception("Автоматические запросы")

        assert "fullTextTranslation" in html
        assert "data-complaint-type" in html

        translation = BeautifulSoup(html, 'html.parser').find('span', attrs={"data-complaint-type": "fullTextTranslation"}).text

    vdisplay.stop()
    return translation

text = '''
This is where tools like Docker really shine. Creating a Docker image and templating containers from it is resource-light and fast. Docker images are also easily reproducible, and can make achieving “infrastructure as code” a feasible reality.
Let’s give it a shot.
Note: All of the following code can be found in my chrome-docker Git project.
Identifying the building blocks
To run a Docker container, we will need a Docker image. An image is a pre-built bundle that contains all of the files and software needed to do the work you are setting out to do. In our case, the Docker image will need to contain:
A basic Bash script (referred to as a ‘bootstrap’ script herein) that will run our startup logic whenever a new container is created from the image
Software required to create a “virtual” display to view Google Chrome
Google Chrome
Since creating a virtual display is not unique to Docker, we can start there and figure out our dependencies along the way.
Writing a bootstrap script
By default, a Docker container does nothing when it is started. To actually do something, we will need to execute some logic whenever a new container is created from the image. Before we build the Docker image, let’s consider what we will need to run a graphical application:
A X server
A window manager
A means to access the container’s display
No display? No fear!
Our first major challenge is the lack of display. This is where Xvfb (X Virtual FrameBuffer) comes in very helpful. Per its man page:
Xvfb is an X server that can run on machines with no display hardware and no physical input devices. It emulates a dumb framebuffer using virtual memory.
Since all of our container’s startup logic will need to run in a single script, we will need to start Xvfb in the background. Something to keep in mind when running anything in the background (Bash background job, or not) is whether or not subsequent operations will need to wait until the first background operation reaches a certain state. In our case, we need our X server to be fully up and running before starting a window manager.
Using the xdpyinfo utility, we can block until the X server is ready. Let’s put it all into a Bash function:
launch_xvfb() {
    # Set defaults if the user did not specify envs.
    export DISPLAY=${XVFB_DISPLAY:-:1}
    local screen=${XVFB_SCREEN:-0}
    local resolution=${XVFB_RESOLUTION:-1280x1024x24}
    local timeout=${XVFB_TIMEOUT:-5}
    # Start and wait for either Xvfb to be fully up,
    # or we hit the timeout.
    Xvfb ${DISPLAY} -screen ${screen} ${resolution} &
    local loopCount=0
    until xdpyinfo -display ${DISPLAY} > /dev/null 2>&1
    do
        loopCount=$((loopCount+1))
        sleep 1
        if [ ${loopCount} -gt ${timeout} ]
        then
            echo "[ERROR] xvfb failed to start."
            exit 1
        fi
    done
}
Running a window manager
Now we have a display — but no window manager. A fantastic solution for this is the light-weight Fluxbox window manager. Similar to our Xvfb logic, we can block until Fluxbox is ready by using the wmctrl utility:
launch_window_manager() {
    local timeout=${XVFB_TIMEOUT:-5}
    # Start and wait for either fluxbox to be fully up or we hit
    # the timeout.
    fluxbox &
    local loopCount=0
    until wmctrl -m > /dev/null 2>&1
    do
        loopCount=$((loopCount+1))
        sleep 1
        if [ ${loopCount} -gt ${timeout} ]
        then
            echo "${G_LOG_E} fluxbox failed to start."
            exit 1
        fi
    done
}
Accessing the virtual display
We will need a way to access the display. A creative solution is to use a VNC server. This can be especially helpful for debugging a container running on a remote system. At this point in the script, we will want to keep the Docker container running as long as the VNC server stays alive:
run_vnc_server() {
    local passwordArgument='-nopw'
    if [ -n "${VNC_SERVER_PASSWORD}" ]
    then
        local passwordFilePath="${HOME}/x11vnc.pass"
        if ! x11vnc -storepasswd "${VNC_SERVER_PASSWORD}" "${passwordFilePath}"
        then
            echo "[ERROR] Failed to store x11vnc password."
            exit 1
        fi
        passwordArgument=-"-rfbauth ${passwordFilePath}"
        echo "[INFO] The VNC server will ask for a password."
    else
        echo "[WARN] The VNC server will NOT ask for a password."
    fi
    x11vnc -display ${DISPLAY} -forever ${passwordArgument} &
    wait $!
}
Bringing the bootstrap logic together
We can bring our Bash logic together now, along with some minor tweaks:

Creating the Docker image
With the bootstrap script completed, we can focus on actually creating the Docker image. This is accomplished by creating a plain text file named Dockerfile. It instructs Docker what to do when building the image.
Docker images have a selectable starting point. Since Ubuntu supports Chrome out of the box, we will use the ubuntu:trusty image as ours. It is important that we update apt-get too — otherwise, we will not be able to install any new packages:
FROM ubuntu:trusty
RUN apt-get update; apt-get clean
We will also want to add a user for running Chrome, since running as root is not allowed by Chrome:
# Add a user for running applications.
RUN useradd apps
RUN mkdir -p /home/apps && chown apps:apps /home/apps
Now we can install required tools, including fluxbox, wmctrl, x11vnc, and xvfb. We will also install wget so we can add the Google signing key to apt-get:
# Install x11vnc.
RUN apt-get install -y x11vnc
# Install xvfb.
RUN apt-get install -y xvfb
# Install fluxbox.
RUN apt-get install -y fluxbox
# Install wget.
RUN apt-get install -y wget
# Install wmctrl.
RUN apt-get install -y wmctrl
# Set the Chrome repo.
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
# Install Chrome.
RUN apt-get update && apt-get -y install google-chrome-stable
Lastly, we need to copy the bootstrap script into the image and tell Docker to run the script when a new container is created from it:
COPY bootstrap.sh /
CMD '/bootstrap.sh'
Bringing together the Dockerfile
Now we can piece together our Docker commands. Make sure to name the file Dockerfile. If you specify a different name, then you will need to explicitly identify it to Docker at build time:

Building the Docker image
With the Dockerfile complete, we can now build an image. This is done using the docker build command. This command will assume that the Dockerfile is actually named ‘Dockerfile’ and is in the current working directory. It takes two arguments:
A unique name for the image, referred to as a “tag”
The path to copy into the “build context”. Be very careful to never specify ‘/’. Doing so will copy your entire machine into the build context!
To build the Docker image, make sure the bootstrap script (named bootstrap.sh) and the Dockerfile are in the same directory and execute the following command:
docker build -t local/chrome:0.0.1 .
After a few minutes, Docker will finish building the image. Running docker images will show you the image name and ID.
Note: If you are looking at my chrome-docker repository, I have automated the build command using an included Gradle project. Building it using Gradle is completely optional; it is only for convenience.
Running the Docker container
Finally, we can create and run a Docker container from the image. Go ahead and give the following command a try:
docker run -p 5900:5900 -e VNC_SERVER_PASSWORD=password --user apps --privileged local/chrome:0.0.1
This will launch a new Docker container and run Xvfb, Fluxbox, and a VNC server. You can access the container’s display by pointing a VNC client to 127.0.0.1.
Note: While the VNC_SERVER_PASSWORD argument is optional, it is not if you are using the macOS VNC viewer. If you do not set a password on macOS, you will not be able to connect to the container’s VNC server.

You can now start Chrome by right clicking the desktop and selecting:
Applications > Network > Web Browsing > Google Chrome

You will be prompted to make Chrome your default browser and whether or not analytics should be sent to Google. Once you answer those questions, you will be able to browse the web using Chrome.

Security concerns
Is running Google Chrome this way more secure then just running Google Chrome directly on your system? Even if it is, there are a few concerns that should not be ignored:
You are accessing the container using VNC. If you are not running a firewall on your machine (or the Docker host), then anyone can potentially watch you browse the web
Google Chrome requires that the --privileged Docker flag be specified. This disables security labeling for the container
Conclusion
Is it possible to run Google Chrome in a Docker container? Yes! Should you do it for testing? Yes! Should you do it to establish a secure browsing session? You can — just make sure you are running a firewall on your machine.
Most of this code can be reused to run other graphical applications in a Docker container. So, why stop at Google Chrome?
'''

t = get_translation(text)
print(t)
