import datetime
import os.path

import reportlab
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch

width, height = letter


class Style:
    def __init__(self, id, data):
        self.id = id
        self.font = data['styles'][id]['font']['name']
        self.size = data['styles'][id]['font']['size']
        self.spacing = data['styles'][id]['spacing']

    def load_font(self, canvas):
        canvas.setFont(self.font, self.size)


def resolve_coordinates(x, y):
    x *= inch
    y *= inch
    if x < 0:
        x += width
    if y < 0:
        y += height
    return x, y


def form(path: str, template: [dict | str], **kwargs):
    # If template is a path, load it into a dict
    if isinstance(template, str):
        with open(template) as file:
            template = dict(yaml.load(file, yaml.Loader))
    # Load styles
    styles = {}
    for key, value in dict(template['styles']).items():
        styles[key] = Style(key, template)

    # Split table input arguments into smaller arguments
    split_arguments = {}
    for argument, value in kwargs.items():
        if isinstance(value, dict):
            for sub_argument, sub_value in value.items():
                final_string = ''
                for string in sub_value:
                    final_string += string + '\\n'
                split_arguments[sub_argument] = sub_value
    kwargs.update(split_arguments)

    # Split tables into their smaller elements
    for element in template['elements']:
        if element['type'] != 'table':
            continue
        # template['elements'] += i['elements']
        for table_element in element['elements']:
            for i in range(len(kwargs[table_element['variable-id']])):
                split_element = table_element.copy()
                del split_element['variable-id']
                split_element['position'] = [split_element['position'][0],
                                             split_element['position'][1] - styles[split_element['style']].spacing * i]
                split_element['content'] = kwargs[table_element['variable-id']][i]
                template['elements'].append(split_element)

        # Add dividers
        if 'divider' not in element.keys():
            continue

        for index in range(0, len(list(kwargs[element['variable-id']].values())[0]) - 1):
            master = element['elements'][0]
            master_style = styles[master['style']]
            divider = dict(element['divider']).copy()
            divider['position'] = [0, master['position'][1] - (
                    master_style.spacing * index + (master_style.size / 72) - .0305555)]
            template['elements'].append(divider)

    # Remove pdf if it already exists
    if os.path.exists(path):
        os.remove(path)

    c = canvas.Canvas(path, pagesize=letter)
    # Iterate through elements and draw them
    for i in template['elements']:
        # If type is data, format it and make it into text
        if i['type'] == 'date':
            if 'format' not in i.keys():
                i['format'] = '%m/%d/%Y'
            if 'variable-id' not in i.keys():
                i['format'] = str(i['format']).replace('\\', '')
                i['content'] = datetime.datetime.now().strftime(i['format'])
            else:
                i['content'] = datetime.datetime.fromtimestamp(kwargs[i['variable-id']]).strftime(i['format'])
            i['type'] = 'text'

        elif 'variable-id' in i.keys():
            i['content'] = kwargs[i['variable-id']]

        if i['type'] == 'money':
            if 'format' not in i.keys():
                i['format'] = '${:.2f}'
            i['content'] = ('-' if float(i['content']) < 0 else '') + i['format'].format(abs(float(i['content'])))
            i['type'] = 'text'

        match str(i['type']):
            case 'text':
                style = styles[i['style']]
                style.load_font(c)
                x, y = resolve_coordinates(float(i['position'][0]), float(i['position'][1]))
                if 'justification' in i.keys() and i['justification'] == 'right':
                    c.drawRightString(x, y, i['content'].strip())
                else:
                    c.drawString(x, y, i['content'].strip())

            case 'multiline-text':
                style = styles[i['style']]
                style.load_font(c)
                x, y = resolve_coordinates(float(i['position'][0]), float(i['position'][1]))
                text = str(i['content']).split('\\n')
                for e in text:
                    if 'justification' in i.keys() and i['justification'] == 'right':
                        c.drawRightString(x, y, e.strip())
                    else:
                        c.drawString(x, y, e.strip())
                    y -= style.spacing * inch

            case 'horizontal-rule':
                offset, y = resolve_coordinates(*i['position'])
                r, g, b = [0, 0, 0] if 'color' not in i.keys() else i['color']
                match i['justification']:
                    case 'right':
                        start_x = width - (i['width'] * inch) - offset
                        end_x = width - offset
                    case 'left':
                        start_x = offset
                        end_x = (i['width'] * inch) + offset
                    case 'center':
                        start_x = (width - (i['width'] * inch)) / 2
                        end_x = start_x + (i['width'] * inch)
                    case _:
                        start_x = (width - (i['width'] * inch)) / 2
                        end_x = start_x + width / 2
                path = c.beginPath()
                path.moveTo(start_x, y)
                path.lineTo(end_x, y)
                # path.close()
                c.setLineWidth(i['stroke'])
                c.setStrokeColorRGB(r, g, b)
                c.drawPath(path)
    c.showPage()
    c.save()
