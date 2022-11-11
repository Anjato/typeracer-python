import pyautogui
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.alert import Alert
import subprocess as sp
import requests

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get('https://play.typeracer.com/')

wait = WebDriverWait(driver, 10)


# function to log in the user with credentials found in creds.txt (same folder as main.py)
# may add encryption later but meh, maybe later
def login():

    # credentials file with username and password
    file = "creds.txt"

    # if file is ABSENT, it will request the user to enter the credentials into the console
    if not os.path.exists(file):
        user = str(input("Please enter username:\n"))
        passwd = str(input("Please enter password:\n"))
        f = open(file, "w")
        f.writelines([user, "\n", passwd])
        f.close()
    # if file is EMPTY,  it will request the user to enter the credentials into the console
    elif os.stat(file).st_size == 0:
        user = str(input("Please enter username:\n"))
        passwd = str(input("Please enter password:\n"))
        f = open(file, "w")
        f.writelines([user, "\n", passwd])
        f.close()
    # opens file and reads username and password from specified lines. I may make this a bit more modular so a person
    # can choose between multiple accounts within the same file
    else:
        f = open(file, "r")
        read = f.readlines()
        user = read[0]
        passwd = read[1]
        f.close()

    # finds the login button
    loginbtn = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '.promptBtn.signIn')))

    # clicks the login button
    loginbtn.click()

    # finds the suername and password text boxes as well as the sign in button
    usernameTextBox = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".gwt-TextBox[name='username'")))
    passwordTextBox = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(2) > td:nth-child(2) "
                                                                              "> table > tbody > tr:nth-child(1) "
                                                                              "> td > input")))
    signInButton = driver.find_element(By.CSS_SELECTOR, ".gwt-Button[type=button]")

    # sends the username and password from the creds.txt file to the appropriate text boxes
    usernameTextBox.send_keys(user)
    alert = Alert(driver)
    # check if random alert pops up and close it
    if alert.text != '':
        alert.accept()
        passwordTextBox.send_keys(passwd)
    else:
        passwordTextBox.send_keys(passwd)

    # clicks the signin button after entering the credentials
    signInButton.click()

    # executs response function
    response()


# main function that complete races. must be on the main page for the function to find the begin race button
def main():
    race = wait.until(ec.presence_of_element_located((By.XPATH, "//a[@class='gwt-Anchor prompt-button bkgnd-green']")))
    race.click()

    go = wait.until(ec.presence_of_element_located((By.XPATH, "//div[@class='gameStatusLabel']")))
    compareList = ["Go!", "The race is on! Type the text below:"]

    changeDisplayFormat = wait.until(
        ec.presence_of_element_located((By.XPATH, "//a[@class='gwt-Anchor display-format-trigger']")))

    changeDisplayFormat.click()
    oldStyleOneRadio = wait.until(
        ec.presence_of_element_located((By.XPATH, "//span[@class='gwt-RadioButton OLD_FULLTEXT']/input")))
    oldStyleOneRadio.click()
    changeDisplayFormatX = wait.until(ec.presence_of_element_located((By.XPATH, "//div[@class='xButton']")))
    changeDisplayFormatX.click()

    words = wait.until(
        ec.presence_of_element_located((By.XPATH, "//div[@class='nonHideableWords unselectable']/span[2]")))

    print(go.text)
    while go.text != compareList[1] and go.text != compareList[0]:
        print(go.text)
        sleep(0.1)

    while go.text == compareList[1] or go.text == compareList[0]:
        try:
            textInput = driver.find_element(By.XPATH, "//input[@class='txtInput']")
            punctuation = driver.find_element(By.XPATH, "//div[@class='nonHideableWords unselectable']/span[3]")
            if punctuation.text != '':
                print(words.text + punctuation.text)
                # pyautogui.write(words.text + ',' + ' ', interval=0.01)
                textInput.send_keys(words.text + punctuation.text + ' ')
                sleep(0.15)
            else:
                print(words.text + punctuation.text)
                # pyautogui.write(words.text + ' ', interval=0.01)
                textInput.send_keys(words.text + ' ')
                sleep(0.15)
        except NoSuchElementException:
            print('Unable to find text field for race. Race finished!\n')
            response()
            pass

    response()


# function to take user input to either start a race (must be on main page) or complete a test to verify typing speed
# will add a check to go to home page if a race is started but the user is not on the home page to find the elements
def response():
    choice = int(input("Are you starting a race (1) or a test (2)?\n"))

    if choice == 1:
        main()
    elif choice == 2:
        test()
        # just in case :)
    elif choice != 1 or 2:
        print("Invalid argument, please try again.")
        sleep(3)
        response()


# uses ocr.space API to send image for OCR
def test():

    api_file = 'api.key'

    f = open(api_file, 'r')
    api_read = f.readlines()
    api_key = api_read[0]


    # vpn()

    begintest = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".gwt-Button.gwt-Button")))
    begintest.click()

    captchaWait = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".challengeImg")))
    challengeTextBox = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".challengeTextArea")))
    submitButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".gwt-Button.gwt-Button")))

    captcha = driver.find_element(By.CSS_SELECTOR, ".challengeImg")
    captcha.screenshot("challenge.png")

    challenge = "challenge.png"

    challengeOCRText = ocr_space_file(filename=challenge, api_key=api_key)
    challengeText = challengeOCRText['ParsedResults'][0]['ParsedText']

    challengeTextBox.send_keys(challengeText)
    submitButton.click()

    response()


def checkvpn():
    os.chdir('C:/Program Files/Private Internet Access/')
    piactl = 'piactl.exe'
    connectionState = sp.Popen([piactl, 'get', 'connectionstate'], stdout=sp.PIPE).communicate()[0]
    return connectionState.decode().strip()


def vpn():
    originaldir = os.getcwd()
    os.chdir('C:/Program Files/Private Internet Access/')
    piactl = 'piactl.exe'
    sp.run([piactl, 'disconnect'])
    sp.run([piactl, 'connect'])

    while True:
        connectionState = checkvpn()
        if connectionState != "Connected":
            checkvpn()
            print(connectionState)
            sleep(1)
        else:
            print("VPN Connected! Continuing...\n")
            break

    os.chdir(originaldir)


def ocr_space_file(filename, overlay=False, api_key='', language='eng', OCREngine=5, scale=True):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :param OCREngine: Optional between 1, 2, 3, or 5
                    1 = fastest, 2 = better with single numbers/characters
                    3 = expands on language support but slower, 5 = seems most accurate
                    Defaults to 1.
    :param scale: API does minor internal upscaling which can significantly improve accuracy
                    Defaults to False.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'OCREngine': OCREngine,
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.json()


# Gets and changes the resolution
def getres():
    width, height = pyautogui.size()
    modW = width / 1.2
    modH = height / 1.2
    driver.set_window_size(modW, modH)

# executes login function
    accountchoice()


def createaccount():
    choice = int(input("Do you want to use PIA VPN to create your account?\n 1 = Yes\n 2 = No\n"))
    vpnstatus = checkvpn()

    if choice == 1:
        if vpnstatus != "Connected":
            vpn()
        else:
            pass
    if choice == 2:
        pass

    create_account = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".promptBtn.createAcct")))
    create_account.click()

    firstName = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".AdvancedTextBox[maxlength='40']:first-child")))
    lastName = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".AdvancedTextBox[maxlength='40']:last-child")))
    email = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".AdvancedTextBox.AdvancedTextBox-unfocused[maxlength='317']")))
    dobMonth = Select(wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".DirtyComboBox.DirtyComboBox-unfocused"))))
    dobYear = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".AdvancedTextBox.AdvancedTextBox-unfocused[maxlength='4']")))
    username = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".gwt-TextBox[size='15']")))
    password = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(16) > td:nth-child(2) > input:nth-child(1)")))
    repeatPassword = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(18) > td:nth-child(2) > input")))
    signUpBtn = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(20) > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > button")))

    firstName.send_keys('First Name')
    lastName.send_keys('Last')
    email.send_keys('email@email.com')
    dobMonth.select_by_index(5)
    dobYear.send_keys('2000')
    username.send_keys('username')
    password.send_keys('password')
    repeatPassword.send_keys('password')
    signUpBtn.click()


def accountchoice():
    choice = int(input("Would you like to create an account (1) or login (2)?\n"))

    if choice == 1:
        createaccount()
    elif choice == 2:
        login()
        # just in case :)
    elif choice != 1 or 2:
        print("Invalid argument, please try again.")
        sleep(3)
        accountchoice()


getres()
