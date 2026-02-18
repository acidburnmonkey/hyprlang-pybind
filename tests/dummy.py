import hyprlang_pybind as hyprlang


def  main():

    schema = {
    "testInt": 0,
    "testFloat": 0.0,
    "testString": "",
    "testVar": 0,
    "testColor": 0,
    "testCategory": {
        "innerInt": 0,
        "innerString": "",
    },
    "testVec": (0.0, 0.0),
    "testBool": 0,
}

    dummy = hyprlang.parse_file('../tests/fixtures/test.conf', schema=schema)
    print('dummy:' , dummy)




if __name__ == '__main__':
    main()
