from odoo import http



class VisaTypeApi(http.Controller):
    @http.route("/api/test",methods=["GET"],type="http", auth="none", csrf=False)
    def test_endpoint(self):
        print("hallo from endpoint")


# class BookLibrary(http.Controller):
#     @http.route('/book_library/book_library', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/book_library/book_library/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('book_library.listing', {
#             'root': '/book_library/book_library',
#             'objects': http.request.env['book_library.book_library'].search([]),
#         })

#     @http.route('/book_library/book_library/objects/<model("book_library.book_library"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('book_library.object', {
#             'object': obj
#         })
