import sys
import requests

if __name__ == '__main__':

    print "This is the name of the script: ", sys.argv[0]
    print "Number of arguments: ", len(sys.argv)
    print "The arguments are: ", str(sys.argv)

    try:

        start = int(sys.argv[1])
        end = int(sys.argv[2])
        url = sys.argv[3]
        headers = {'Range': 'bytes=%d-%d' % (start, end)}

        print headers

        r = requests.get(url, headers=headers, stream=True)

        file_name = str(start) + '-' + str(end)

        fp = open('/tmp/' + file_name, "wb")
        fp.write(r.content)
        fp.close()

    except Exception as e:
        print "error in server script {}".format(e.message)


