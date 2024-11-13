"""
# ==========================================================
 File: ContentExport.py
 Description: Script that use the Canvas API Library - this file
   retrieves all content from the Canvas Modules view into an HTML Document
   to serve as a Redesign Course Blueprint

   TODO: Remove extraneous modules/data
   TODO: Replace terminal output with logging
   TODO: Add error handling
   TODO: Google API integration
   TODO: Make nice....

  Author: Justin Mello
  Date: 2024-11-07
  Version: 1.0
  ==========================================================
"""

# import all dependencies
from canvasapi import Canvas
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup





#create all html header data for doc conversion
#TODO get rid of style sheet and just inline
html_meta = """<!doctype html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Hello World!</title>
                    <meta name="description" content="">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="stylesheet" href="style.css">
                </head>"""

def convert_headings(text):
    """Convert HTML headings to Blueprint formatting"""
    soup = BeautifulSoup(text, 'html.parser')

    #Remove all heading tags, append them in color: Red; > (H#) < format
    for heading_level in range(1, 7):
        heading_tag = f'h{heading_level}'
        headings = soup.find_all(heading_tag)

        for heading in headings:
            # Create new paragraph tag
            paragraph = soup.new_tag('p')
            # Create span tag for the heading level
            span = soup.new_tag('span', style='color:red; font-weight: bold;')
            span.string = f' (H{heading_level})'

            # Set the paragraph's text content
            paragraph['style'] = 'font-family: Arial; font-size: 11pt;'
            paragraph.string = heading.text
            # Append the span to the paragraph
            paragraph.append(span)

            # Replace the heading with the new paragraph
            heading.replace_with(paragraph)

    return str(soup)

def init_canvas():
    """Creates Canvas API Connection"""
    #TODO add some error handling

    # Loads all environment variables
    load_dotenv()

    # instantiates canvas object with canvas url & api token
    # canvas url and api token are stored in a safe .env file
    return Canvas(os.getenv('BASE_URL'), os.getenv('API_TOKEN'))

#TODO: Refactor this crap
def process_items(item, course, file):
    """Handle different item types and output"""
    if item.type == "Assignment":  # grab content, write to file
        assignment = course.get_assignment(item.content_id)
        file.write(f"<h4 style=\"font-family: Arial; font-size: 14pt;\">{assignment.name}</h4>\n")
        file.write(f'<p style="color:red; font-weight: bold; font-size: 11pt;">{item.type}</p>\n')
        file.write(f"{convert_headings(assignment.description)}\n")
    elif item.type == "Page":
        page = course.get_page(item.page_url)
        file.write(f"<h3 style=\"font-family: Arial; font-size: 14pt;\">{page.title}</h3>\n")
        file.write(f'<p style="color:red; font-weight: bold; font-size: 11pt;">{item.type}</p>\n')
        # f.write(f"{page.body}\n")
        file.write(f"{convert_headings(page.body)}\n")
    elif item.type == "Discussion":
        discussion = course.get_discussion_topic(item.content_id)
        file.write(f"<h4 style=\"font-family: Arial; font-size: 14pt;\">{discussion.title}</h4>\n")
        file.write(f'<p style="color:red; font-weight: bold; font-size: 11pt;">{item.type}</p>\n')
        # f.write(f"{discussion.message}\n")
        file.write(f"{convert_headings(discussion.message)}\n")
    elif item.type == "Quiz":
        quiz = course.get_quiz(item.content_id)
        file.write(f"<h4 style=\"font-family: Arial; font-size: 14pt;\">{quiz.title}</h4>\n")
        file.write(f'<p style="color:red; font-weight: bold; font-size: 11pt;">{item.type}</p>\n')
        # f.write(f"{quiz.description}\n")
        file.write(f"{convert_headings(quiz.description)}\n")
    elif item.type == "File":
        file.write(f"<h4 style=\"font-family: Arial; font-size: 14pt;\">{item.title}<h4>\n")
    elif item.type == "ExternalUrl":
        file.write(
            f"<h4 style=\"font-family: Arial; font-size: 14pt;\"><a href=\"{item.external_url}\">{item.title}</a></h4>\n")
        file.write(
            f'<p style="color:red; font-weight: bold; font-size: 11pt;">Unpublished External Link; Load in a new tab</p>\n')
    elif item.type == "SubHeader":
        file.write(
            f"<hr style=\"color:blue;\"><h3 style=\"font-family: Arial; font-size: 15pt;color:blue;\">{item.title}</h3><hr style=\"color:blue;\">\n")

def course_export(course_number):
    #create canvas object, get course
    canvas = init_canvas()
    course = canvas.get_course(course_number)

    # grabs all modules in a paginated list
    modules = course.get_modules()

    '''
           creates the html document, currently just appends data
           needs to create document for each course and/or wipe each html file
           before extending to google
           '''

    file_name = "BlueprintRedesign.html"  # name sucks
    print(f"Creating {file_name}")  # terminal output for now
    # Open a file to append data to
    with open(file_name, 'a', encoding="utf-8") as f:
        # enable as html document with appropriate tags/encoding
        f.write(f"{html_meta}\n")
        '''
        This currently doesn't work, need to read the front_page and syllabus info documentation
        TODO grab front page
        f.write(f"<h3>Home</h3>\n{course.get_page('front_page').body}\n")
        TODO grab syllabus
        f.write(f"<h3>Syllabus/h3>\n{course.get_assignment('syllabus').body}\n") 
        '''

        # fetches module...
        for module in modules:  # loop through all course modules
            f.write(f"<h2>{module.name}</h2>\n")  # write module name...need to fix heading hierarchy
            module_items = module.get_module_items()
            for item in module_items:  # loop through all module items
               #Get item specific details
               process_items(item, course, f)
            print(f"Processed {module.name} ")  # output to terminal

        # closes html document
        f.write("</body>\n</html>")


def main():
    """Runs the script"""
    course_input = input("Enter the course number: ")
    course_export(course_input)

if __name__ == '__main__':
    main()
