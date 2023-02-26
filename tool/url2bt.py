# sudo apt-get install python-libtorrent
# !/usr/bin/env python
import os.path as pt
import shutil
import sys
import tempfile
from time import sleep

import libtorrent as lt


def magnet2torrent(magnet, output_name=None):
    if output_name and \
            not pt.isdir(output_name) and \
            not pt.isdir(pt.dirname(pt.abspath(output_name))):
        print("Invalid output folder: " + pt.dirname(pt.abspath(output_name)))
        print("")
        sys.exit(0)
    tempdir = tempfile.mkdtemp()
    ses = lt.session()
    params = {
        'save_path': tempdir,
        'duplicate_is_error': True,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True
    }
    handle = lt.add_magnet_uri(ses, magnet, params)
    print("Downloading Metadata (this may take a while)")
    while (not handle.has_metadata()):
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Aborting...")
            ses.pause()
            print("Cleanup dir " + tempdir)
            shutil.rmtree(tempdir)
            sys.exit(0)
    ses.pause()
    print("Done")
    torinfo = handle.get_torrent_info()
    torfile = lt.create_torrent(torinfo)
    output = pt.abspath(torinfo.name() + ".torrent")
    if output_name:
        if pt.isdir(output_name):
            output = pt.abspath(pt.join(
                output_name, torinfo.name() + ".torrent"))
        elif pt.isdir(pt.dirname(pt.abspath(output_name))):
            output = pt.abspath(output_name)
    print("Saving torrent file here : " + output + " ...")
    torcontent = lt.bencode(torfile.generate())
    f = open(output, "wb")
    f.write(lt.bencode(torfile.generate()))
    f.close()
    print("Saved! Cleaning up dir: " + tempdir)
    ses.remove_torrent(handle)
    shutil.rmtree(tempdir)
    return output


def showHelp():
    print("")
    print("USAGE: " + pt.basename(sys.argv[0]) + " MAGNET [OUTPUT]")
    print(" MAGNET\t- the magnet url")
    print(" OUTPUT\t- the output torrent file name")
    print("")


def main():
    if len(sys.argv) < 2:
        showHelp()
        sys.exit(0)
    magnet = sys.argv[1]
    output_name = None
    if len(sys.argv) >= 3:
        output_name = sys.argv[2]
    magnet2torrent(magnet, output_name)


if __name__ == "__main__":
    main()

    # python Magnet_To_Torrent2.py <magnet link> [torrent file]
    # import libtorrent as bt
# info = bt.torrent_info('test.torrent')
# print "magnet:?xt=urn:btih:%s&dn=%s" % (info.info_hash(), info.name())
