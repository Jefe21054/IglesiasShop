from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'

class ClienteForm(forms.Form):
    
    SEXO_CHOICES = (
        ('M','Masculino'),
        ('F','Femenino'),
        ('N','No Especificar'),
    )
    
    cedula = forms.CharField(label='CÉDULA',max_length=10)
    nombre = forms.CharField(label='NOMBRE',max_length=200,required=True)
    apellidos = forms.CharField(label='APELLIDOS',max_length=200,required=True)
    email = forms.EmailField(label='EMAIL',required=True)
    direccion = forms.CharField(label='DIRECCIÓN',widget=forms.Textarea)
    telefono = forms.CharField(label='TELÉFONO',max_length=20)
    sexo = forms.ChoiceField(label='SEXO',choices=SEXO_CHOICES)
    fecha_nacimiento = forms.DateField(label='FECHA DE NACIMIENTO',input_formats=['%Y-%m-%d'],widget=DateInput())
