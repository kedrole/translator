from django import forms
from .models import Page, Article
from django.forms import ModelChoiceField

class PageEditForm(forms.ModelForm):
    #domain_name = forms.CharField(label='Доменное имя', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Page
        fields = ('domain_name', 'content_tag_name', 'content_property_name', 'content_property_value', 'content_page')
        widgets = {
            'domain_name': forms.TextInput(attrs={'class': 'form-control'}),
            'content_page': forms.TextInput(attrs={'class': 'form-control'}),

            'content_tag_name': forms.TextInput(attrs={'class': 'form-control'}),
            'content_property_name': forms.TextInput(attrs={'class': 'form-control'}),
            'content_property_value': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ArticleEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class PageChoiceField(ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.content_page

    #domain_name = forms.CharField(label='Доменное имя', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    page = PageChoiceField(queryset=Page.objects.all(), empty_label=None)#, attrs={'class': 'form-control'}),

    class Meta:
        model = Article
        fields = ('title', 'page', 'status', 'original_unique_proc')
        #widgets = {
        #    'status': forms.Select(attrs={'class': 'form-control'}),
        #}


