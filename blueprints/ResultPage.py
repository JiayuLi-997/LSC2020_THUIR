from flask import *
from flask_wtf import FlaskForm #基类
from wtforms import BooleanField,TextAreaField,StringField,PasswordField,RadioField,SelectField, IntegerField,SubmitField
from . import searchclass#,auto_input
from . import util
from flask import session,g
from whoosh import analysis
import calendar
import numpy as np
import time
import cv2
home = Blueprint("search_result",__name__,url_prefix="/result")

@home.route('/',methods=['GET','POST'])
def display_result():
    s_time = time.time()
    if request.method == 'POST' and request.form.get('form_fill') :
        # click "Fill the forms"
        mySearch = searchclass.SearchClass()
        real_tags = {}
        text = request.form.get('text_input')
        if text:
            # [parsed_query,real_tags] = g.searcher.QueryParser(text,'info_dictionary_mar8.json')
            [parsed_query,real_tags] = mySearch.QueryParser(text,'info_dictionary_mar8.json')
            if 'query_term' in session:
                # session['query_term'] = util.merge(session['query_term'],parsed_query,session['parsed_query'])
                # print(session['query_term'],parsed_query,session['parsed_query'])
                session['this_parsed_query'] = parsed_query
                query_term = util.merge(session['query_term'],parsed_query,session['all_parsed_query'])
            else:
                # session['query_term'] = parsed_query
                session['this_parsed_query'] = parsed_query
                query_term = parsed_query
                session['all_parsed_query'] = {}
            # session['query_term']['text'] = text
            query_term['text'] = text
            # session['parsed_query'] = parsed_query
            session['real_tags'] = real_tags
            # session['js_query_term'] = util.js_query(session['query_term'])
            session['js_query_term'] = util.js_query(query_term)
        mySearch.__close__()
        print('query parse time: %f s'%(round(time.time()-s_time,2)))
        return render_template('ResultPage.html',all_content={'js_query_term':session['js_query_term'],'result_key':session['result_key'],
                                                             'result_all':session['result_all'],'extra_info':session['extra_info']})
    elif request.method == 'POST' and request.form.get('search') :
        # click "Search"
        mySearch = searchclass.SearchClass()
        this_query,img_feedback_str, tag_feedback_str= \
            util.get_query_term(dict(request.form),{'shot_id':session['shot_id'],'result_key':session['result_key'],'extra_info':session["extra_info"]})
        for key in this_query:
            if 'location' in key and type(this_query[key]) != dict:
                this_query[key] = list(set(this_query[key]))
        session['all_parsed_query'] = util.merge(session['all_parsed_query'],session['this_parsed_query'],session['all_parsed_query'])
        # [img_key_list, img_all_list,shot_id_dict,session['extra_info']] = g.searcher.QueryMain(util.add_tags(this_query,session['real_tags']))
        [img_key_list, img_all_list,shot_id_dict,session['extra_info']] = mySearch.QueryMain(util.add_tags(this_query,session['real_tags']),limit_num=15)
        mySearch.__close__()

        session['query_term'] = this_query
        # session["query_term"]["img_feedback_str"] = img_feedback_str
        # session["query_term"]["tag_feedback_str"] = tag_feedback_str
        session['query_term']['text'] = request.form.get('text_input')
        session['result_key'] = img_key_list
        session['result_all'] = img_all_list
        session['shot_id'] = dict( shot_id_dict, **session['shot_id'])
        # session['js_query_term'] = util.js_query(session['query_term'],img_feedback_str,tag_feedback_str)
        # session['js_query_term'] = util.js_query(session['query_term'],img_feedback_str,tag_feedback_str)
        print('search time: %f s'%(round(time.time()-s_time,2)))
        # print('query term:::')
        # print(session['query_term'])
        # print(session['js_query_term'])
        return render_template('ResultPage.html',all_content={'js_query_term':session['js_query_term'],'result_key':session['result_key'],
                                                             'result_all':session['result_all'],'extra_info':session['extra_info']})
    else:
        session['js_query_term'] = util.js_query(session['query_term'])
        print(session['js_query_term'])
        return render_template('ResultPage.html',all_content={'js_query_term':session['js_query_term'],'result_key':session['result_key'],
                                                             'result_all':session['result_all'],'extra_info':session['extra_info']})