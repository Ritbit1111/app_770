from bokeh.models import Slider, CustomJS, Label
from bokeh.layouts import row, column
from bokeh.plotting import Figure, ColumnDataSource
from bokeh.models.widgets import Button, TextInput
from bokeh.models import Span
from os.path import dirname, join
from . import iv

def plot_iv(doc):

    init_calc = iv.iv_data(72, 800, 25, 45.9, 9.25, 37.2, 8.76, 7.47, 100)
    source = ColumnDataSource(data=init_calc[0])
    source_translated = ColumnDataSource(data=init_calc[1])
    res_source = ColumnDataSource(data=init_calc[2])
    status_param = init_calc[3]
    print(status_param)

    plot = Figure(plot_width = 600, plot_height = 600, y_range = (-1, 10), x_range = (0,60))
    plot.xaxis.axis_label = 'Voltage (V)'
    plot.yaxis.axis_label = 'Current (I)'
    plot.scatter('x', 'y', source=source, line_width=3, line_alpha=0.6, )
    plot.scatter('x', 'y', source=source_translated, line_width=3, line_alpha=0.6, line_color='red', )
    
    sig_plot = Figure(plot_width=300, 
                        plot_height=300, 
                        x_axis_label='Series Resistance (Rs)',
                        y_axis_label='Shunt Resistance (Rsh)',
                        title = 'Calculated Resistances')
    sig_plot.scatter('x', 'y', source=res_source, line_width=10)
    vline = Span(location=0, dimension='height', line_color='red', line_width=3)
    # Horizontal line
    hline = Span(location=0, dimension='width', line_color='green', line_width=3)
    sig_plot.renderers.extend([vline, hline])


    error_plt = Figure(plot_width=100, 
                        plot_height=50, 
                        toolbar_location = None,)

    if (status_param.success==True):
        print ('Successful Entry to the landing page')
        cite = Label(text='Success', render_mode='css', text_color='white', border_line_color='green', background_fill_color='green')
    else:
        print ('Inside fail')
        cite = Label(text='False', render_mode='css', text_color='white', border_line_color='red', background_fill_color='red')
    error_plt.add_layout(cite)
    error_plt.add_layout(Label(text='Success', render_mode='css', text_color='white', border_line_color='green', background_fill_color='green'))


    Ncell_input = TextInput(value='72', title='No. of cells')
    Irrad_input = TextInput(value='800', title='Irradiance')
    Temp_input = TextInput(value='25', title='Temperature (Celcius)')
    Isc_input = TextInput(value='9.25', title='I_sc at STC')
    Im_input = TextInput(value='8.76', title='I_m')
    Voc_input = TextInput(value='45.9', title='V_oc')
    Vm_input = TextInput(value='37.2', title='V_m')
    Isc_N_input = TextInput(value='7.47', title='I_sc at NOTC(G=800, T=45C)')
    Data_input = TextInput(value='100', title='Data Size')
    submit = Button(label='Submit', button_type='success')
    download_button_STC = Button(label = 'Download data (STC)')
    download_button_GT = Button(label = 'Download data (Translated)')
    
    def get_inputs():
        return (float(Ncell_input.value) ,float(Irrad_input.value) ,float(Temp_input.value) ,float(Voc_input.value) ,float(Isc_input.value), float(Vm_input.value), float(Im_input.value), float(Isc_N_input.value), float(Data_input.value))
    
    def update_plot(event):
        N, G, T, V, I, Vm, Im, I_N, datapoints = get_inputs()
        print ('#'*30)
        print ('Updating the plot')
        print ('#'*30)
        updated_data = iv.iv_data(N, G, T, V, I, Vm, Im, I_N, datapoints)
        source.data = updated_data[0]
        source_translated.data = updated_data[1]
        res_source.data = updated_data[2]
        global status_param
        status_param = updated_data[3]
        print(status_param)
        if (status_param.success==True):
            print ('Inside success')
            cite = Label(text='Successful Parameter Extraction', render_mode='css', text_color='white', border_line_color='green', background_fill_color='green')
        else:
            print ('Inside fail')
            cite = Label(text='Parameter extraction not converging', render_mode='css', text_color='white', border_line_color='red', background_fill_color='red')
        error_plt = Figure(plot_width=100, 
                        plot_height=50, 
                        toolbar_location = None,)

        error_plt.add_layout(cite)
        layout.children[2].children[1] = error_plt

    def update_success():
        if (status_param.success==True):
            print ('Inside success')
            cite = Label(text='Success', render_mode='css', text_color='white', border_line_color='green', background_fill_color='green')
        else:
            print ('Inside fail')
            cite = Label(text='False', render_mode='css', text_color='white', border_line_color='red', background_fill_color='red')
        error_plt = Figure(plot_width=100, 
                        plot_height=50, 
                        toolbar_location = None,)

        error_plt.add_layout(cite)
        layout.children[2].children[1] = error_plt


    submit.on_click(update_plot)
    download_button_STC.js_on_click(CustomJS(args=dict(source=source),code=open(join(dirname(__file__), "download.js")).read()))
    download_button_GT.js_on_click(CustomJS(args=dict(source=source_translated),code=open(join(dirname(__file__), "download.js")).read()))
    
    #doc.add_periodic_callback(update_success, 1000)

    layout = row(plot, column(Ncell_input, Irrad_input, Temp_input, Isc_input, Im_input, Voc_input, Vm_input,Isc_N_input,  Data_input, submit, download_button_STC, download_button_GT), column(sig_plot, error_plt))
    return (layout)

