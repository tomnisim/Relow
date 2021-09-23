# from Object.UserService import UserService
# from Object.CategoryService import CategoryService
# from Object.StepService import StepService
# from Object.SubCategoryService import SubCategoryService
# from Object.OfferService import OfferService
# from Object.ProductService import ProductService
from BusinessLayer.Controllers.CategoryController import CategoryController
from Service.Object.CategoryService import CategoryService
from BusinessLayer.Controllers.UserController import UserController
from Response import Response

from Service.Object.OfferService import OfferService
from Service.Object.UserService import UserService

from BusinessLayer.Object.Step import Step


class Handler:

    def __init__(self, conn):
        self.conn = conn
        self.user = None

        self.category_controller = CategoryController.getInstance()
        self.user_controller = UserController.getInstance()
        self.switcher = {1: self.register,
                         2: self.unregister,
                         3: self.log_in,
                         4: self.logout,
                         5: self.update,
                         6: self.update_password,
                         # 7: self.update_user_name,
                         # 8: self.update_email,
                         # 9: self.update_birth_date,
                         # 10: self.update_gender,
                         11: self.add_address_details,
                         12: self.add_payment_method,
                         13: self.get_all_history_buy_offers,
                         14: self.get_all_history_sell_offers,
                         15: self.update_offer,
                         # 16: self.get_history_sell_offer,
                         17: self.get_all_active_buy_offers,
                         18: self.get_all_active_sell_offers,
                         # 19: self.get_active_buy_offer,
                         # 20: self.get_active_sell_offer,
                         # 21: self.get_liked_offer,
                         22: self.get_all_liked_offers,
                         23: self.add_active_buy_offer,
                         24: self.add_active_sell_offer,
                         25: self.add_liked_offer,
                         26: self.remove_liked_offer,
                         27: self.remove_active_sell_offer,
                         28: self.remove_active_buy_offer,
                         29: self.add_category,
                         30: self.add_sub_category,
                         31: self.add_photo,
                         32: self.remove_category,
                         33: self.remove_sub_category,
                         34: self.remove_photo,
                         35: self.update_category_name,
                         36: self.update_sub_category_name,
                         37: self.update_purchase,
                         #  check 38
                         38: self.update_sub_category_for_offer,
                         39: self.update_end_date,
                         40: self.update_start_date,
                         41: self.update_step,
                         42: self.update_product_name,
                         43: self.update_product_company,
                         44: self.update_product_colors,
                         45: self.update_product_sizes,
                         46: self.update_product_description,
                         47: self.get_offers_by_category,
                         48: self.get_offers_by_sub_category,
                         49: self.get_offers_by_product_name,
                         # 50: self.get_offers_by_status,
                         51: self.get_hot_deals,
                         52: self.add_to_hot_deals,
                         53: self.remove_from_hot_deals,
                         54: self.update_step_for_offer,
                         55: self.exit,
                         56: self.get_all_categories,
                         78 : self.guest_register,
                         79 : self.guest_login,
                         80: self.merge_register,
                         81: self.complete_register,
                         94: self.contact_us,
                         99: self.get_offers_by_product_company,
                         500: self.confirm_add_active_sell_offer,
                         501: self.confirm_remove_active_sell_offer}


    # ------------------------------------------------userController----------------------------------------------------

    # -------------------------------------------------BASIC------------------------------------------------------------
    def guest_register(self, argument):
        try:
            user = self.user_controller.guest_register()
            self.user = user
            return Response({'user_id': user.user_id,'liked_offers': []}, 'guest registered Successfully', True)
        except Exception as e:
            return Response(None, str(e), False)

    def guest_login(self, argument):
        to_return = []
        try:
            ans = self.user_controller.guest_login(argument['guest_id'])
            # offers_list = ans['liked_offers']
            # for offer in offers_list:
            #     temp = vars(OfferService(offer))
            #     if offer.confirm:
            #         to_return.append(temp)
            self.user = ans['user']
            return Response({'liked_offers': to_return}, 'guest login Successfully', True)
        except Exception as e:
            return Response(None, str(e), False)

    def unregister(self, argument):
        try:
            self.user_controller.unregister(self.user.user_id)
            return Response(None, 'Unregistered Successfully', True)
        except Exception as e:
            return Response(None, str(e), False)

    def register(self, argument):
        try:
            user = self.user_controller.register(
                argument['first_name'],
                argument['last_name'],
                argument['user_name'],
                argument['email'],
                argument['password'],
                argument['birth_date'],
                argument['gender'])
            self.user = user
            return Response(vars(UserService(user)), "Registered Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def merge_register(self, argument):
        # this method register user after he use the system as a guest - and merge the info about him
        try:
            user = self.user_controller.merge_register(
                argument['user_id'],
                argument['first_name'],
                argument['last_name'],
                argument['user_name'],
                argument['email'],
                argument['password'],
                argument['birth_date'],
                argument['gender'])
            self.user = user
            return Response(vars(UserService(user)), "Registered Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def log_in(self, argument):
        try:
            user = self.user_controller.log_in(argument['user_name'], argument['password'])
            self.user = user
            return Response(vars(UserService(user)), "Log-In Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def logout(self, argument):
        try:
            user_id = self.user.user_id
            self.user_controller.logout(user_id)
            return Response(None, "Log-Out Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # -------------------------------------------------ADD------------------------------------------------------------------

    def add_active_buy_offer(self, argument):
        try:
            offer = self.category_controller.get_offer_by_offer_id(argument['offer_id'])
            self.user_controller.add_active_buy_offer(self.user.user_id, offer, argument['quantity'], argument['step'],
                                                      argument['color'], argument['size'], argument['address'])
            return Response(OfferService(offer), "Joined To Offer Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def add_active_sell_offer(self, argument):
        steps = self.build_steps(argument['steps'])
        if self.user is None:
            return Response(None, "not logged in motek", False)
        offer = None
        try:
            offer = self.category_controller.add_offer(self.user.user_id,
                                                       argument['name'],
                                                       argument['company'],
                                                       argument['colors'],
                                                       argument['sizes'],
                                                       argument['description'],
                                                       argument['photos'],
                                                       argument['category_name'],
                                                       argument['sub_category_name'],steps,
                                                       # argument['steps'],
                                                       argument['end_date'], False)
            self.user_controller.add_active_sale_offer(offer)
            return Response(OfferService(offer), "Offer Added Successfully", True)
        except Exception as e:
            if str(e) == "wow":
                self.category_controller.remove_offer(offer)
            return Response(None, str(e), False)

    def add_liked_offer(self, argument):
        try:
            offer = self.category_controller.get_offer_by_offer_id(argument['offer_id'])
            self.user_controller.add_like_offer(self.user.user_id, offer)
            return Response(OfferService(offer), "Offer Added SuccessfullyTo Liked Offers", True)
        except Exception as e:
            return Response(None, str(e), False)

    def add_address_details(self, argument):
        try:
            self.user_controller.add_address_details(self.user.user_id,
                                                     argument['city'],
                                                     argument['street'],
                                                     argument['zip_code'],
                                                     argument['floor'],
                                                     argument['apt'])
            return Response(None, "Address Details Added Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # def update_city(argument): user_id *
    # def update_street(argument): user_id *
    # def update_zip_code(argument): user_id *
    # def update_floor(argument): user_id *
    # def update_apt(argument): user_id *

    def add_payment_method(self, argument):
        try:
            self.user_controller.add_payment_method(self.user.user_id,
                                                    argument['credit_card_number'],
                                                    argument['expire_date'],
                                                    argument['cvv'],
                                                    argument['card_type'],
                                                    argument['id_number'])
            return Response(None, "Payment Added Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # def update_card_number(argument): user_id *
    # def update_expire_date(argument): user_id *
    # def update_cvv(argument): user_id *
    # def update_id_number user_id *
    # def update_card_type(argument): user_id *
    # -------------------------------------------------REMOVE------------------------------------------------------------------

    def remove_liked_offer(self, argument):
        try:
            self.user_controller.remove_like_offer(self.user.user_id, argument['offer_id'])
            return Response(None, "Offer Removed From Liked Offers", True)
        except Exception as e:
            return Response(None, str(e), False)

    def remove_active_sell_offer(self, argument):
        try:
            offer = self.category_controller.remove_offer(argument['offer_id'])
            self.user_controller.remove_active_sale_offer(offer)
            return Response(OfferService(offer), "Offer Removed Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def remove_active_buy_offer(self, argument):
        try:
            self.user_controller.remove_active_buy_offer(self.user.user_id, argument['offer_id'])
            return Response(None, "Offer Removed Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # -------------------------------------------------UPDATE----------------------------------------------------------------
    def update_offer(self, argument):
        if self.user is None:
            return Response(None, "not logged in motek", False)
        exceptions = []
        try:
            self.user_controller.update_end_date(argument['user_id'],argument['offer_id'], argument['end_date'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_product_name(argument['user_id'],argument['offer_id'], argument['name'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_product_company(argument['user_id'],argument['offer_id'], argument['company'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_product_colors(argument['user_id'],argument['offer_id'], argument['colors'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_product_sizes(argument['user_id'],argument['offer_id'], argument['sizes'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_product_description(argument['user_id'],argument['offer_id'], argument['description'])
        except Exception as e:
            exceptions.append(str(e))

        steps = self.build_steps(argument['steps'])
        for step_number in steps.keys():
            try:
                self.category_controller.update_step_for_offer(argument['offer_id'], step_number,
                                                               steps[step_number].limit,steps[step_number].price)
            except Exception as e:
                exceptions.append(str(e))

        try:
            offer = self.category_controller.update_sub_category_for_offer(argument['offer_id'],
                                            argument['category_name'],argument['sub_category_name'])
        except Exception as e:
            exceptions.append(str(e))

        return Response(vars(OfferService(offer)), exceptions, True)

    def update(self, argument):
        if self.user is None:
            return Response(None, "not logged in motek", False)
        exceptions = []

        try:
            self.user_controller.update_first_name(self.user.user_id, argument['first_name'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_last_name(self.user.user_id, argument['last_name'])
        except Exception as e:
            exceptions.append(str(e))

        try:
            self.user_controller.update_email(self.user.user_id, argument['email'])
        except Exception as e:
            exceptions.append(str(e))

        finally:
            user = self.user_controller.get_user_by_id(self.user.user_id)
            return Response(vars(UserService(user)), exceptions, True)

    #
    #
    # def update_first_name(self, argument):
    #     try:
    #         self.user_controller.update_first_name(self.user.user_id, argument['first_name'])
    #         return Response(None, "First Name Updated Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def update_last_name(self, argument):
    #     try:
    #         self.user_controller.update_last_name(self.user.user_id, argument['last_name'])
    #         return Response(None, "Last Name Updated Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def update_user_name(self, argument):
    #     try:
    #         self.user_controller.update_username(self.user.user_id, argument['user_name'])
    #         return Response(None, "Username Updated Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def update_email(self, argument):
    #     try:
    #         self.user_controller.update_email(self.user.user_id,
    #                                           argument['email'])
    #         return Response(None, "Email Updated Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    def update_password(self, argument):
        try:
            self.user_controller.update_password(self.user.user_id,
                                                 argument['old_password'],
                                                 argument['new_password'])
            return Response(None, "Password Updated Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # def update_birth_date(self, argument):
    #     try:
    #         self.user_controller.update_birth_date(self.user.user_id,
    #                                                argument['birth_date'])
    #         return Response(None, "Birth Date Updated Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def update_gender(self, argument):
    #     try:
    #         self.user_controller.gender(self.user.user_id,
    #                                     argument['gender'])
    #         return Response(None, "gender Updated Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)

    # -------------------------------------------------GET------------------------------------------------------------------

    def get_all_history_buy_offers(self, argument):
        lis = []
        try:
            offer_list = self.user_controller.get_history_buy_offers(self.user.user_id)
            for offer in offer_list:
                temp = vars(OfferService(offer))
                lis.append(temp)
            return Response(lis, 'All History buy Offers', True)
        except Exception as e:
            return Response(None, str(e), False)

    def get_all_history_sell_offers(self, argument):
        lis = []
        try:
            offers_list = self.user_controller.get_history_sell_offers(self.user.user_id)
            for offer in offers_list:
                temp = vars(OfferService(offer))
                lis.append(temp)
            return Response(lis, 'All History sell Offers', True)
        except Exception as e:
            return Response(None, str(e), False)

    # def get_history_buy_offer(self, argument):
    #     try:
    #         offer = self.user_controller.get_history_buy_offer(argument['offer_id'])
    #         return Response(vars(OfferService(offer)), "Got offer Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def get_history_sell_offer(self, argument):
    #     try:
    #         offer = self.user_controller(argument['offer_id'])
    #         return Response(vars(OfferService(offer)), "Got Offer Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)

    def get_all_active_buy_offers(self, argument):
        lis = []
        try:
            offer_buy_list = self.user_controller.get_active_buy_offers(self.user.user_id)
            for offer in offer_buy_list:
                temp = vars(OfferService(offer))
                lis.append(temp)
            return Response(lis, "All Active Buy Offers", True)
        except Exception as e:
            return Response(None, str(e), False)

    def get_all_active_sell_offers(self, argument):
        lis = []
        try:
            offer_sell_list = self.user_controller.get_active_sale_offers(self.user.user_id)
            for offer in offer_sell_list:
                temp = vars(OfferService(offer))
                lis.append(temp)
            return Response(lis, "All Active Sell Offers", True)
        except Exception as e:
            return Response(None, str(e), False)

    # def get_active_buy_offer(self, argument):
    #     try:
    #         offer = self.user_controller.get_buy_offer(self.user.user_id, argument['offer_id'])
    #         return Response(vars(OfferService(offer)), "Got Offer Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def get_active_sell_offer(self, argument):
    #     try:
    #         offer = self.user_controller.get_sell_offer(self.user.user_id, argument['offer_id'])
    #         return Response(vars(OfferService(offer)), "Got Offer Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)
    #
    # def get_liked_offer(self, argument):
    #     try:
    #         offer = self.user_controller.get_liked_offer(self.user.user_id, argument['offer_id'])
    #         return Response(vars(OfferService(offer)), "Update Sub-Category Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)

    def get_all_liked_offers(self, argument):
        lis = []
        try:
            liked_offers_list = self.user_controller.get_liked_offers(self.user.user_id)
            for offer in liked_offers_list:
                temp = vars(OfferService(offer))
                lis.append(temp)
            return Response(lis, "All Liked Offers", True)
        except Exception as e:
            return Response(None, str(e), False)

    # --------------------------------------------------categoryController-------------------------------------------------------

    # -----------------------------------------------------ADD-------------------------------------------------------------------

    def add_category(self, argument):
        try:
            self.category_controller.add_category(argument['name'])
            return Response(None, "Category Added Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def add_sub_category(self, argument):
        try:
            self.category_controller.add_sub_category(argument['name'], argument['category_name'])
            return Response(None, "Sub-Category Added Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def add_photo(self, argument):
        pass

    def add_to_hot_deals(self, argument):
        response = self.category_controller.add_to_hot_deals(argument['offer_id'])
        return response

    # ------------------------------------------------REMOVE------------------------------------------------------------

    def remove_category(self, argument):
        try:
            self.category_controller.remove_category(argument['category_name'])
            return Response(None, "Category Removed Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def remove_sub_category(self, argument):
        try:
            self.category_controller.remove_category(argument['sub_category_name'],
                                                     argument['category_name'])
            return Response(None, "Sub-Category Removed Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def remove_photo(self, argument):
        pass

    def remove_from_hot_deals(self, argument):
        try:
            self.category_controller.remove_from_hot_deals(argument['offer_id'])
            return Response(None, "Offer Removed Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # -------------------------------------------------------UPDATE----------------------------------------------------------------------
    def update_category_name(self, argument):
        try:
            self.category_controller.update_category_name(argument['category_name'],
                                                          argument['name'])
            return Response(None, "Category Name Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_sub_category_name(self, argument):
        try:
            self.category_controller.update_sub_category_name(argument['category_name'],
                                                              argument['sub_category_name'],
                                                              argument['name'])
            return Response(None, "Update Sub-Category Name Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_sub_category_for_offer(self, argument):
        try:
            offer = self.category_controller.update_sub_category_for_offer(argument['offer_id'],
                                                                           argument['category_name'],
                                                                           argument['sub_category_name'])
            return Response(OfferService(offer), "Update Category Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_end_date(self, argument):
        try:
            self.user_controller.update_end_date(argument['offer_id'], argument['end_date'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_start_date(self, argument):
        try:
            self.user_controller.update_start_date(argument['offer_id'], argument['start_date'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_step(self, argument):
        try:
            self.user_controller.update_step_for_user(self.user.user_id, argument['offer_id'], argument['step'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_product_name(self, argument):
        try:
            self.user_controller.update_product_name(argument['offer_id'], argument['name'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_product_company(self, argument):
        try:
            self.user_controller.update_product_company(argument['offer_id'], argument['company'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_product_colors(self, argument):
        try:
            self.user_controller.update_product_colors(argument['offer_id'], argument['colors'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_product_sizes(self, argument):
        try:
            self.user_controller.update_sizes(argument['offer_id'], argument['sizes'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_product_description(self, argument):
        try:
            self.user_controller.update_product_description(argument['offer_id'], argument['description'])
            return Response(None, "Update Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # -------------------------------------------------------GET---------------------------------------------------------------

    def get_offers_by_category(self, argument):
        to_return = []
        try:
            offers_list = self.category_controller.get_offers_by_category(argument['category_name'])
            for offer in offers_list:
                temp = vars(OfferService(offer))
                if offer.confirm:
                    to_return.append(temp)
            return Response(to_return, "Offers Lists (by category) Received Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def get_offers_by_sub_category(self, argument):
        to_return = []
        try:
            offers_list = self.category_controller.get_offers_by_sub_category(argument['category_name'],
                                                                              argument['sub_category_name'])
            for offer in offers_list:
                temp = vars(OfferService(offer))
                if offer.confirm:
                    to_return.append(temp)
            return Response(to_return, "Offers Lists (by sub category) Received Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def get_offers_by_product_name(self, argument):
        to_return = []
        try:
            offers_list = self.category_controller.get_offers_by_product_name(argument['name'])
            for offer in offers_list:
                temp = vars(OfferService(offer))
                if offer.confirm:
                    to_return.append(temp)
            return Response(to_return, "Offers Lists (by product name) Received Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # def get_offers_by_status(self, argument):
    #     to_return = []
    #     try:
    #         offers_list = self.category_controller.get_offers_by_status(argument['status'])
    #         for offer in offers_list:
    #             temp = vars(OfferService(offer))
    #             to_return.append(temp)
    #         return Response(to_return, "Offers Lists Received Successfully", True)
    #     except Exception as e:
    #         return Response(None, str(e), False)

    def get_hot_deals(self, argument):
        to_return = []
        try:
            offers_list = self.category_controller.get_hot_deals()
            for offer in offers_list:
                temp = vars(OfferService(offer))
                if offer.confirm:
                    to_return.append(temp)
            return Response(to_return, "Offers Lists (hot deals) Received Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    # -----------------------------------------------------------------------------------------------------------------

    def update_step_for_offer(self, argument):
        try:
            self.category_controller.update_step_for_offer(argument['offer_id'], argument['step_number'],
                                                           argument['quantity'], argument['price'])
            return Response(None, "Step Updated Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def get_all_categories(self, argument):
        # not sure we need the try
        try:
            ans = []
            categories = self.category_controller.get_all_categories()
            for cat in categories:
                ans.append(vars(CategoryService(cat)))
            return Response(ans, "all categories names", True)
        except Exception as e:
            return Response(None, str(e), False)

    def update_purchase(self, argument):
        try:
            self.remove_active_buy_offer(argument)
            self.add_active_buy_offer(argument)
            return Response(None, "purchase Updated Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def complete_register(self, argument):
        code = argument['code']
        user_id = self.user.user_id
        if code == user_id:
            try:
                self.user_controller.complete_register(user_id)
                return Response(None, 'good confirmation', True)
            except Exception as e:
                    return Response(None, str(e), False)
        else:
            return Response(None, 'the code is incorrect', False)

    def get_offers_by_product_company(self, argument):
        to_return = []
        try:
            offers_list = self.category_controller.get_offers_by_company_name(argument['company'])
            for offer in offers_list:
                temp = vars(OfferService(offer))
                if offer.confirm:
                    to_return.append(temp)
            return Response(to_return, "Offers Lists (by product company) Received Successfully", True)
        except Exception as e:
            return Response(None, str(e), False)

    def contact_us(self, argument):
        try:
            msg = argument['subject'] + ":\n " + argument['description'] + "\n user_id:" + str(self.user.user_id)
            message = """\
            Subject: contact from client

            """ + msg
            self.user_controller.emailHandler.sendemail("shareit1256@gmail.com", message)
            return Response(True, "contact good", True)
        except Exception as e:
            return Response(None, str(e), False)

    def handling(self, argument):
        req = argument['op']
        func = self.switcher.get(int(req), "nada")
        ans = func(argument)
        print(ans.res)
        print(ans.data)

        return ans

    def exit(self):
        print("exit")
        return Response(None, "EXIT", None)

    def build_steps(self, steps):
        ans = {}
        for step in steps:
            ans[step['step_number']] = Step(step['limit'],step['price'])
        return ans

    def confirm_add_active_sell_offer(self, argument):
        self.category_controller.get_offer_by_offer_id(argument['offer_id']).confirm = True

    def confirm_remove_active_sell_offer(self, argument):
        offer = self.category_controller.get_offer_by_offer_id(argument['offer_id'])
        self.user_controller.remove_active_sale_offer(offer)