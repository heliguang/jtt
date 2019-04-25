import json
from django.views.generic.base import View
from django.http import HttpResponse

from jtt808.protocol.jtt_2011_808 import decode_hex_string


class DecodeView(View):
    def get(self, request):
        key_words = request.GET.get('s','')
        if key_words:
            re_datas = decode_hex_string(key_words)
        else:
            re_datas = {'错误' : '解析内容为空!!!'}
        return HttpResponse(json.dumps(re_datas), content_type="application/json")