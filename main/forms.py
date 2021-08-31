from django import forms
from .models import Site, ListPage, Article
from django.forms import ModelChoiceField

class SiteEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Site
        fields = ('domain_name', 'content_tag_name', 'content_property_name', 'content_property_value', 'preview_tag_name', 'preview_tag_property_name', 'preview_tag_property_value')


class ListPageEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class SiteChoiceField(ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.domain_name

    site = SiteChoiceField(queryset=Site.objects.all(), empty_label=None)

    class Meta:
        model = ListPage
        fields = ('site', 'href')


class ArticleEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class ListPageChoiceField(ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.site.domain_name + " -> " + ("Главная" if obj.href == "" else obj.href)

    list_page = ListPageChoiceField(queryset=ListPage.objects.all(), empty_label=None)#, attrs={'class': 'form-control'}),

    class Meta:
        model = Article
        fields = ('title', 'list_page', 'status', 'original_unique_percent')
        #widgets = {
        #    'status': forms.Select(attrs={'class': 'form-control'}),
        #}


