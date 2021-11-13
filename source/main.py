from server import MyServer
from client import MyClient

def main():
    print('====== MENU ======')
    print('1. Create server')
    print('2. Join server')
    print('==================')
    c = input('Enter your choice: ')
    if c=='1':
        MyServer()
    elif c=='2':
        MyClient()
    else:
        print('Invalid choice!')

if __name__ == '__main__':
    main()