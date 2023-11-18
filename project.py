
import speech_recognition as sr
from openai import OpenAI
import os
import sys
from PIL import Image
import requests
from io import BytesIO
import re
from validator_collection import validators, checkers, errors
from fpdf import FPDF
from email.message import EmailMessage
import ssl 
import smtplib

client = OpenAI(
  api_key=os.getenv("SECRET_API_KEY"),  # this is also the default, it can be omitted
)

def send_mail(user_name,pdf_name,user_email):
    pdf_name=pdf_name.replace(" ","_")
    email_sender="munimthahmid2@gmail.com"
    email_password=os.getenv("EMAIL_PASSWORD")

    email_receiver=user_email
    subject=f"Hi {user_name}!"
    body="""
    Thanks for talking with TalkGPT. Here is your transcript!

"""
    em=EmailMessage()

    em['From']=email_sender
    em['To']=email_receiver
    em['subject']=subject
    em.set_content(body)

    pdf_path = pdf_name  # Replace with the actual path to your PDF file
    with open(pdf_path, 'rb') as pdf_file:
        em.add_attachment(pdf_file.read(), maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))

    context=ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())
    


def voice_to_text(prompt="Speak something:",recognizer=None):
    if recognizer==None:
        recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(prompt)
        audio = recognizer.listen(source, timeout=5)

        try:
            # Use Google Web Speech API to convert audio to text
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"Error with the API request: {e}")
            return ""
def generate_response(prompt):
    # Make a request to the ChatGPT API

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=prompt
    )

    assistant_reply = response.choices[0].message.content
    return assistant_reply

def generate_image(transcript,user_name):
    recognizer = sr.Recognizer()
 
    
    with sr.Microphone() as source:
            print("Describe the image you want!.")

            audio = recognizer.listen(source, timeout=5)


            try:
                text = recognizer.recognize_google(audio)
                insert_text_to_pdf(f"{user_name}: {text}",transcript)
                image=client.images.generate(
        prompt=text,
        n=1,
        size="256x256"
    )           
                image_url=image.data[0].url
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img.show()
                img.save(f"{text}.png")
                insert_image_to_pdf(f"{text}.png",transcript)
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Error with the API request; {e}")



def talk_with_me(user_name,transcript):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    while True:
        user_input = voice_to_text("What you want to talk with me about?")
        if "stop chat" in user_input:
            break

        if not user_input:
            continue  # Skip if unable to recognize speech

        conversation.append({"role": "user", "content": user_input})

        assistant_reply = generate_response(conversation)

        print(f"{user_name}: ",user_input)
        insert_text_to_pdf(f"{user_name}: {user_input}",transcript)
        print("TalkGPT:", assistant_reply)
        insert_text_to_pdf(f"TalkGPT: {assistant_reply}",transcript)
   
        conversation.append({"role": "assistant", "content": assistant_reply})
def show_options():
    
      print("""
          Here are the list of thing I can do.\n
          1.Image Generation\n
          2.Talk With You\n
          
          
          """)
      
def get_name():
    user_name = input("Great. Let's get friend. What's your name?").strip()

    if not user_name or re.search(r"\d", user_name):
        raise ValueError
    else:
        return user_name
        



def get_email():
    while True:
        try:
            email_address = validators.email(input("What's your email?"))
        
        except errors.InvalidEmailError:
            print("Invalid Email")
            break
        except errors.EmptyValueError:
            print("Invalid Email")
            break
        
        else:
            break
        
    return email_address
def insert_text_to_pdf(text,transcript):
    y=int(transcript.get_y())
    transcript.set_xy(0,y)
    transcript.multi_cell(0,10,text)
    y=int(transcript.get_y())+10
    transcript.set_xy(0,y)
    
    
    
def insert_image_to_pdf(image_path,transcript):
    image_height = 50
    transcript.image(image_path, y=int(transcript.get_y())+10, h=image_height)
    transcript.set_xy(0,transcript.get_y()+image_height)
    
    y=int(transcript.get_y())+30
    transcript.set_xy(5,y)
    
    
def main():
    command=input("Hey There! I am TalkGPT! I can do so so so many thing. Do you want to play with me?")
    if "no" in command:
        sys.exit("Sorry to hear that 😒")
        
    user_name=get_name()   
    user_email=get_email()
    
    
    transcript = FPDF(orientation="portrait", format="A4")
    transcript.set_font('helvetica', size=12)

    transcript.add_page()
    transcript.cell(0, 10, 'TalkGPT Transcript', 0, 1, 'C')
    
    
    show_options()
    recognizer = sr.Recognizer()
    start_command = input("Type 'start' to begin recording: ")
    if start_command.lower() == 'start':
        while True:
            text=voice_to_text("Which one do you want to do?")
            if "image generation" in text.lower():
                generate_image(transcript,user_name)
            elif "talk with you" in text.lower():
                talk_with_me(user_name,transcript)
                        
            elif "exit" in text:
                    print(f"Goodbye {user_name}")
                    transcript.output(f"{user_name}'s_Transcript.pdf")
                    send_mail(user_name,f"{user_name}'s Transcript.pdf",user_email)
                    sys.exit("Your transcript has been sent to your email. Have a nice day!")
    








if __name__=="__main__":
    main()