def html_wrapper(content):
  css = """#wrapper {
	  padding:0px;
	  width:900px;
	  max-width: 100%;
	  margin: 0 auto;
	  border:1px solid #000000;
	
	  -moz-border-radius-bottomleft:0px;
	  -webkit-border-bottom-left-radius:0px;
	  border-bottom-left-radius:0px;
	
	  -moz-border-radius-bottomright:0px;
	  -webkit-border-bottom-right-radius:0px;
	  border-bottom-right-radius:0px;
	
	  -moz-border-radius-topright:0px;
	  -webkit-border-top-right-radius:0px;
	  border-top-right-radius:0px;
	
	  -moz-border-radius-topleft:0px;
	  -webkit-border-top-left-radius:0px;
	  border-top-left-radius:0px;
  }
  #wrapper table{
    border-collapse: collapse;
    border-spacing: 0;
	  width:100%;
	  margin:0px;padding:0px;
  }
  #wrapper tr:last-child td:last-child {
	  -moz-border-radius-bottomright:0px;
	  -webkit-border-bottom-right-radius:0px;
	  border-bottom-right-radius:0px;
  }
  #wrapper table tr th {
	  -moz-border-radius-topleft:0px;
	  -webkit-border-top-left-radius:0px;
	  border-top-left-radius:0px;
  }
  #wrapper table tr:first-child td:last-child {
	  -moz-border-radius-topright:0px;
	  -webkit-border-top-right-radius:0px;
	  border-top-right-radius:0px;
  }
  #wrapper tr th {
	  -moz-border-radius-bottomleft:0px;
	  -webkit-border-bottom-left-radius:0px;
	  border-bottom-left-radius:0px;
  }
  #wrapper tr:hover td{
	
  }
  #wrapper tr:nth-child(even){ background-color:#e5e5e5; }
  #wrapper tr:nth-child(odd){ background-color:#b2b2b2; }
  #wrapper td{
	  vertical-align:middle;
	  border:1px solid #000000;
	  border-width:0px 1px 1px 0px;
	  text-align:left;
	  padding:7px;
	  font-size:14px;
	  font-family:Arial;
	  font-weight:normal;
	  color:#000000;
  }
  #wrapper tr:last-child td{
	  border-width:0px 1px 1px 0px;
  }
  #wrapper tr td:last-child{
	  border-width:0px 0px 1px 0px;
  }
  #wrapper tr:last-child td:last-child{
	  border-width:0px 0px 1px 0px;
  }
  #wrapper tr th{
		  background:-o-linear-gradient(bottom, #7f7f7f 5%, #cccccc 100%);	background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #7f7f7f), color-stop(1, #cccccc) );
	  background:-moz-linear-gradient( center top, #7f7f7f 5%, #cccccc 100% );
	  filter:progid:DXImageTransform.Microsoft.gradient(startColorstr="#7f7f7f", endColorstr="#cccccc");	background: -o-linear-gradient(top,#7f7f7f,cccccc);
    padding: 4px 0px;
	  background-color:#7f7f7f;
	  border:0px solid #000000;
	  text-align:center;
	  border-width:1px 1px 1px 1px;
	  font-size:18px;
	  font-family:Arial;
	  font-weight:bold;
	  color:#000000;
  }
  #wrapper tr:hover th {
	  background:-o-linear-gradient(bottom, #7f7f7f 5%, #cccccc 100%);	background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #7f7f7f), color-stop(1, #cccccc) );
	  background:-moz-linear-gradient( center top, #7f7f7f 5%, #cccccc 100% );
	  filter:progid:DXImageTransform.Microsoft.gradient(startColorstr="#7f7f7f", endColorstr="#cccccc");	background: -o-linear-gradient(top,#7f7f7f,cccccc);

	  background-color:#7f7f7f;
  }
  #wrapper tr th:first-child{
	  border-width:1px 0px 1px 0px;
  }
  #wrapper tr th:last-child{
	  border-width:1px 0px 1px 1px;
  }
  #caption {
    padding: 10px 5px;
  }
"""

  return '<html><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type"><style>'+ css +'</style></head><body><div id="wrapper">'+content+'</div></body></html'

def html_table(headers = [], rows = [], caption = ''):
  return '<table>'+html_header(headers)+html_body(rows)+'</table>'+html_caption(caption)

def html_header(headers):
  return '<thead><tr>'+''.join(map(lambda h: '<th>'+h+'</th>',headers))+'</tr></thead>'

def html_body(rows):
  html = '<tbody>'
  for values in rows:
    html += '<tr>'+''.join(map(lambda td: "<td>" + td + "</td>", values))+'</tr>'
  return html+'</tbody>'

def html_caption(caption):
  if caption:
    return '<div id="caption">'+caption+'</div>'
  else:
    return ''
