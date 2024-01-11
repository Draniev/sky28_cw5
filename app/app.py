from art import tprint
from app.ui.user_interface import UserInterface


def main():
    tprint('HP API APP', font='univerce')

    ui = UserInterface()
    ui.start()
    tprint('^^^^^^', font='univerce')


if __name__ == "__main__":
    main()
