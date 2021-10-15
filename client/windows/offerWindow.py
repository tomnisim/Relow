import csv
import io
import pandas as pd
from kivy.uix.gridlayout import GridLayout
from Utils.Utils import Utils
from kivy.app import App
from kivy.uix.image import Image, CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.dropdown import DropDown
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField, MDTextFieldRound
# from Backend_controller import Backend_controller
from Service.Object.OfferService import OfferService

from windows.paymentWindow import PAYMENTScreen


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


class OfferScreen(Screen):
    def __init__(self, **kwargs):
        super(OfferScreen, self).__init__(**kwargs)
        self.name = "offer_screen"

    def init_offer(self, offer, photo_lis):
        self.name = self.name + str(offer[0].offer_id)
        self.controller = App.get_running_app().controller
        self.offer = offer[0]  # Offer Service
        self.offer_id = self.offer.offer_id
        self.color = 0
        self.num_of_quantity = 0
        self.change = False
        self.new_address = None
        # buyer/seller/viewer/user
        self.user = self.controller.user_service

        if self.controller.guest is True:
            self.show_as_guest(photo_lis)
        elif self.offer.is_a_seller(self.user.user_id):
            self.show_as_seller(photo_lis)
        elif self.user.is_a_buyer(self.offer.offer_id):
            self.show_as_buyer(photo_lis)
        else:
            self.show_as_viewer(photo_lis)
        return

    def show_as_guest(self, photo_lis):
        print('as a guest')
        self.box = BoxLayout(orientation='vertical')
        # back button
        self.back = MDIconButton(icon="windows/images/back_btn.png")
        self.back.bind(on_press=lambda x: self.out())
        self.box.add_widget(self.back)
        # photo list
        self.carousel = Carousel(size_hint_y=1)
        self.insert_photos(self.carousel, photo_lis)
        self.box.add_widget(self.carousel)
        # steps
        self.slider = MDSlider()
        self.slider.min = 0
        self.slider.max = 150
        self.slider.value = 15
        steps = self.offer.steps
        # for step in steps:
        #     pass
        self.slider.min = 0
        self.slider.max = 100  # steps[-1][1]
        self.slider.value = 10  # self.offer.current_buyers
        self.steps_box = BoxLayout(orientation='vertical', size_hint_y=.4)
        self.progress = MDProgressBar()
        self.progress.value = self.slider.value
        self.people_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            self.people_per_step.add_widget(
                MDLabel(text='people:' + str(step.get_buyers_amount()) + "/" + str(step.get_limit())))
        self.steps_box.add_widget(self.people_per_step)
        self.steps_box.add_widget(self.progress)
        self.price_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            x = MDCheckbox(group="price", size_hint_x=.1)
            x.bind(active=self.set_total_price)
            self.price_per_step.add_widget(x)
            self.price_per_step.add_widget(MDLabel(text="price: " + str(step.get_price())))
        self.steps_box.add_widget(self.price_per_step)
        self.box.add_widget(self.steps_box)

        # labels box
        self.labels_icons = BoxLayout(orientation='horizontal')
        self.labels_icons.size_hint_y = 0.5
        self.labels_box = BoxLayout(orientation='vertical')
        self.name1 = MDLabel(text=" " + self.offer.product.name)
        self.name1.bold = True
        self.name1.font_size = 22.0
        self.name1.color = (0, 0, 0, 1)
        self.labels_box.add_widget(self.name1)
        self.company = MDLabel(text="  " + self.offer.product.company)
        self.company.color = (0, 0, 0, 0.27)
        self.labels_box.add_widget(self.company)
        self.description = MDLabel(text="  " + self.offer.product.description)
        self.description.color = (0, 0, 0, 0.27)
        self.labels_box.add_widget(self.description)
        self.labels_icons.add_widget(self.labels_box)
        # icons box
        self.icons_box = BoxLayout(orientation='horizontal')
        if self.user.is_a_liker(self.offer_id):
            self.like = MDIconButton(icon="windows/images/unlike.png")
        else:
            self.like = MDIconButton(icon="windows/images/like.png")
        self.like.bind(on_press=lambda x: self.like_unlike())
        self.icons_box.add_widget(self.like)
        self.icons_box.padding = [250, 0, 0, 0]
        self.labels_icons.add_widget(self.icons_box)
        self.box.add_widget(self.labels_icons)

        # colors and sizes
        self.color_size = BoxLayout(orientation='vertical')
        # self.color_size.spacing= 25
        self.box.add_widget(self.color_size)
        self.chosen_colors = {}
        self.chosen_sizes = {}

        # price
        self.curr_price = MDLabel(text="price")
        self.curr_price.size_hint_y = 0.2
        self.box.add_widget(self.curr_price)

        self.add_item()

        # join button
        self.join_offer = BoxLayout(orientation='horizontal')
        self.join_offer.size_hint_y = 0.2
        self.join = Button(text="JOIN")
        self.join.size_hint_y = 0.2
        self.join.background_color = (24 / 255, 211 / 255, 199 / 255, 1)
        self.join.bind(on_press=lambda x: self.guest_try_to_join())
        self.box.add_widget(self.join_offer)
        self.box.add_widget(self.join)
        self.add_widget(self.box)

    def show_as_seller(self, photo_lis):
        print("as a seller")
        self.title = self.offer.product.name
        self.box = BoxLayout(orientation='vertical')
        self.carousel = Carousel(size_hint_y=6)
        self.insert_photos(self.carousel, photo_lis)
        self.box.add_widget(self.carousel)
        self.slider = MDSlider()
        self.slider.min = 0
        self.slider.max = 150
        self.slider.value = 15
        steps = self.offer.steps
        # for step in steps:
        #     pass
        self.slider.min = 0
        self.slider.max = 100  # steps[-1][1]
        self.slider.value = 10  # self.offer.current_buyers
        self.progress = MDProgressBar()
        self.progress.value = self.slider.value
        self.people_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            self.people_per_step.add_widget(
                MDLabel(text='people:' + str(step.get_buyers_amount()) + "/" + str(step.get_limit())))
        self.box.add_widget(self.people_per_step)
        self.box.add_widget(self.progress)
        self.price_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            self.price_per_step.add_widget(MDCheckbox(group="price", size_hint_x=.1))
            self.price_per_step.add_widget(MDLabel(text="price: " + str(step.get_price())))
        self.box.add_widget(self.price_per_step)
        self.name1 = Label(text=self.offer.product.name)
        self.box.add_widget(self.name1)
        self.company = Label(text=self.offer.product.company)
        self.box.add_widget(self.company)
        self.description = Label(text=self.offer.product.description)
        self.box.add_widget(self.description)
        self.color_dropdown = DropDown()
        colors = self.offer.product.colors
        for color in colors:
            btn = Button(text=' % s' % color, size_hint=(None, None), height=40)
            btn.bind(on_release=lambda btn: self.color_dropdown.select(btn.text))
            self.color_dropdown.add_widget(btn)
        self.color_mainbutton = Button(text='colors', size_hint=(None, None), pos=(350, 300))
        self.color_mainbutton.bind(on_release=self.color_dropdown.open)
        self.color_mainbutton = Button(text='colors', size_hint=(None, None), pos=(350, 300))
        self.color_mainbutton.bind(on_release=self.color_dropdown.open)
        self.color_box = BoxLayout(orientation='horizontal')
        self.color_box.add_widget(self.color_mainbutton)
        # self.box.add_widget(self.color_box)

        self.color_dropdown.bind(on_select=lambda instance, x: setattr(self.color_mainbutton, 'text', x))

        self.size_dropdown = DropDown()
        sizes = self.offer.product.sizes
        for size in sizes:
            btn = Button(text=' % s' % size, size_hint=(None, None), height=40)
            btn.bind(on_release=lambda btn: self.size_dropdown.select(btn.text))
            self.size_dropdown.add_widget(btn)
        self.size_mainbutton = Button(text='sizes', size_hint=(None, None), pos=(400, 300))
        self.size_mainbutton.bind(on_release=self.size_dropdown.open)
        # self.box.add_widget(self.size_mainbutton)
        self.size_dropdown.bind(on_select=lambda instance, x: setattr(self.size_mainbutton, 'text', x))
        self.join_offer = BoxLayout(orientation='horizontal')
        # self.quantity = MDTextField(hint_text='QUANTITY')
        self.update = Button(text="UPDATE")
        self.update.bind(on_press=lambda x: self.update_offer())
        # self.join_offer.add_widget(self.quantity)
        self.join_offer.add_widget(self.update)
        self.remove_offer_bt = Button(text="REMOVE OFFER")
        self.remove_offer_bt.bind(on_press=lambda x: self.remove_offer())
        # self.join_offer.add_widget(self.quantity)
        self.join_offer.add_widget(self.remove_offer_bt)
        self.box.add_widget(self.join_offer)
        self.back = Button(text="BACK")
        self.back.bind(on_press=lambda x: self.out())
        self.box.add_widget(self.back)
        self.add_widget(self.box)

    def show_as_buyer(self, photo_lis):
        print('as a buyer')
        purchases = self.offer.get_current_buyers()
        purchase = None
        for purch in purchases:
            p = purchases[purch]
            if p.buyer_id == self.user.user_id:
                self.purchase = p
                break
        self.title = self.offer.product.name
        self.box = BoxLayout(orientation='vertical')
        self.carousel = Carousel(size_hint_y=6)
        # for photo in photo_lis:
        #     self.carousel.add_widget(photo)
        # image = AsyncImage(source="windows/images/a.png")
        # self.carousel.add_widget(image)
        self.insert_photos(self.carousel, photo_lis)
        self.box.add_widget(self.carousel)
        self.slider = MDSlider()
        self.slider.min = 0
        self.slider.max = 150
        self.slider.value = 15
        steps = self.offer.steps

        self.slider.min = 0
        self.slider.max = 100  # steps[-1][1]
        self.slider.value = 10  # self.offer.current_buyers
        self.progress = MDProgressBar()
        self.progress.value = self.slider.value
        self.people_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            self.people_per_step.add_widget(
                MDLabel(text='people:' + str(step.get_buyers_amount()) + "/" + str(step.get_limit())))
        self.box.add_widget(self.people_per_step)
        self.box.add_widget(self.progress)
        self.price_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            if self.purchase.step_id == step.step_number:
                self.price_per_step.add_widget(MDCheckbox(group="price", size_hint_x=.1, active=True))
            else:
                self.price_per_step.add_widget(MDCheckbox(group="price", size_hint_x=.1))
            self.price_per_step.add_widget(MDLabel(text="price: " + str(step.get_price())))

        self.box.add_widget(self.price_per_step)

        self.name1 = Label(text=self.offer.product.name)
        self.box.add_widget(self.name1)
        self.company = Label(text=self.offer.product.company)
        self.box.add_widget(self.company)
        self.description = Label(text=self.offer.product.description)
        self.box.add_widget(self.description)

        self.color_size = BoxLayout(orientation='horizontal')
        self.box.add_widget(self.color_size)

        size_lis = self.split_str(self.purchase.size)
        color_lis = self.split_str(self.purchase.color)
        self.color_mainbutton = {}
        self.size_mainbutton = {}
        self.chosen_colors = self.list_to_dict(color_lis)
        self.chosen_sizes = self.list_to_dict(size_lis)

        for i in range(1, len(color_lis) + 1):
            self.chosen_colors[i] = color_lis[i - 1]
            self.chosen_sizes[i] = size_lis[i - 1]
        self.color_dropdown = {}
        self.size_dropdown = {}
        self.another_item = Button(text="another item")
        self.another_item.bind(on_press=lambda x: self.add_item())
        self.box.add_widget(self.another_item)
        self.remove = Button(text="less item")
        self.remove.bind(on_press=lambda x: self.remove_item())
        self.box.add_widget(self.remove)
        quan = self.purchase.quantity
        for i in range(0, quan):
            self.add_item_for_update(color_lis[i], size_lis[i])

        self.join_offer = BoxLayout(orientation='horizontal')
        self.unjoin = Button(text="CANCEL")
        self.unjoin.bind(on_press=lambda x: self.cancel_purchase())
        self.update = Button(text="UPDATE")
        self.update.bind(on_press=lambda x: self.update_purchase())
        self.join_offer.add_widget(self.unjoin)
        self.join_offer.add_widget(self.update)
        self.box.add_widget(self.join_offer)

        self.back = Button(text="BACK")
        self.back.bind(on_press=lambda x: self.out())
        self.box.add_widget(self.back)

        if self.user.is_a_liker(self.offer_id):
            self.like = Button(text="UNLIKE")
        else:
            self.like = Button(text="LIKE")
        self.like.bind(on_press=lambda x: self.like_unlike())
        self.box.add_widget(self.like)
        self.add_widget(self.box)

    def show_as_viewer(self, photo_lis):
        print('as a viewer')
        self.box = BoxLayout(orientation='vertical')
        # back button
        self.back = MDIconButton(icon="windows/images/back_btn.png")
        self.back.bind(on_press=lambda x: self.out())
        self.box.add_widget(self.back)
        # photo list
        self.carousel = Carousel(size_hint_y=1)
        self.insert_photos(self.carousel, photo_lis)
        self.box.add_widget(self.carousel)
        # steps
        self.slider = MDSlider()
        self.slider.min = 0
        self.slider.max = 150
        self.slider.value = 15
        steps = self.offer.steps
        # for step in steps:
        #     pass
        self.slider.min = 0
        self.slider.max = 100  # steps[-1][1]
        self.slider.value = 10  # self.offer.current_buyers
        self.steps_box = BoxLayout(orientation='vertical', size_hint_y=.4)
        self.progress = MDProgressBar()
        self.progress.value = self.slider.value
        self.people_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            self.people_per_step.add_widget(
                MDLabel(text='people:' + str(step.get_buyers_amount()) + "/" + str(step.get_limit())))
        self.steps_box.add_widget(self.people_per_step)
        self.steps_box.add_widget(self.progress)
        self.price_per_step = BoxLayout(orientation='horizontal', size_hint_y=.2)
        for step_id in steps:
            step = steps[step_id]
            x = MDCheckbox(group="price", size_hint_x=.1)
            x.bind(active=self.set_total_price)
            self.price_per_step.add_widget(x)
            self.price_per_step.add_widget(MDLabel(text="price: " + str(step.get_price())))
        self.steps_box.add_widget(self.price_per_step)
        self.box.add_widget(self.steps_box)

        # labels box
        self.labels_icons = BoxLayout(orientation='horizontal')
        self.labels_icons.size_hint_y = 0.5
        self.labels_box = BoxLayout(orientation='vertical')
        self.name1 = MDLabel(text=" "+self.offer.product.name)
        self.name1.bold = True
        self.name1.font_size = 22.0
        self.name1.color = (0, 0, 0, 1)
        self.labels_box.add_widget(self.name1)
        self.company = MDLabel(text="  "+self.offer.product.company)
        self.company.color = (0, 0, 0, 0.27)
        self.labels_box.add_widget(self.company)
        self.description = MDLabel(text="  "+self.offer.product.description)
        self.description.color = (0, 0, 0, 0.27)
        self.labels_box.add_widget(self.description)
        self.labels_icons.add_widget(self.labels_box)
        # icons box
        self.icons_box = BoxLayout(orientation='horizontal')
        self.another_item = MDIconButton(icon="windows/images/add.png")
        self.another_item.bind(on_press=lambda x: print(self.add_item()))
        self.icons_box.add_widget(self.another_item)
        self.remove = MDIconButton(icon="windows/images/minus.png")
        self.remove.bind(on_press=lambda x: self.remove_item())
        self.icons_box.add_widget(self.remove)
        if self.user.is_a_liker(self.offer_id):
            self.like = MDIconButton(icon="windows/images/unlike.png")
        else:
            self.like = MDIconButton(icon="windows/images/like.png")
        self.like.bind(on_press=lambda x: self.like_unlike())
        self.icons_box.add_widget(self.like)
        self.icons_box.padding = [250,0,0,0]
        self.labels_icons.add_widget(self.icons_box)
        self.box.add_widget(self.labels_icons)

        # colors and sizes
        self.color_size = BoxLayout(orientation='vertical')
        # self.color_size.spacing= 25
        self.box.add_widget(self.color_size)
        self.chosen_colors = {}
        self.chosen_sizes = {}

        # price
        self.curr_price = MDLabel(text="price")
        self.curr_price.size_hint_y = 0.2
        self.box.add_widget(self.curr_price)

        self.add_item()

        # join button
        self.join_offer = BoxLayout(orientation='horizontal')
        self.join_offer.size_hint_y = 0.2
        self.join = Button(text="JOIN")
        self.join.size_hint_y = 0.2
        self.join.background_color = (24 / 255, 211 / 255, 199 / 255, 1)
        self.join.bind(on_press=lambda x: self.join_())
        # another address button
        self.other_address = Button(text='NEW ADDRESS FOR THIS PRODUCT')
        self.other_address.bind(on_press=lambda x: self.add_address())
        self.join_offer.add_widget(self.other_address)
        self.box.add_widget(self.join_offer)
        self.box.add_widget(self.join)
        self.add_widget(self.box)

    # as a guest
    def guest_try_to_join(self):
        Utils.pop(self, 'Hello! guest have to register before buy', 'alert')

    # as a viewer

    def set_total_price(self, a, b):
        step_id = self.get_step()
        if step_id == -1:
            total_price = 0
        else:
            step = self.offer.steps[step_id]
            price_per_step = step.get_price()
            total_price = self.num_of_quantity * price_per_step
        self.curr_price.text = "  price : " + str(total_price)

    def chose_color(self, btn, text, num_of_quantity, color_num):
        print("chosen color:"+str(text)+"\n"+"num_of_quantity:"+str(num_of_quantity)+"\n")
        # change color of all the other button to the regular color
        y = btn.parent
        for ch in y.children:
            ch.icon = "windows/images/colors/un_" + self.get_btn_color(ch) + ".png"
        # change color of the selected button
        btn.icon = "windows/images/colors/" + text + ".png"
        # chosen colors for add offer
        self.chosen_colors[num_of_quantity] = text

    def chose_size(self, btn, text, num_of_quantity, size_num):
        # change color of all the other button to the regular button color
        y = btn.parent
        for ch in y.children:
            ch.background_color = [1, 1, 1, 1]
        # change size of the selected button
        btn.background_color = (24 / 255, 211 / 255, 199 / 255, 1)
        # chosen sizes for add offer
        self.chosen_sizes[num_of_quantity] = text

    def get_btn_color(self, btn):
        str = btn.icon
        ans = str[22:len(str)-4]
        if ans[0:3] =="un_":
            ans = ans[3:len(ans)]
        return ans

    def remove_item(self):
        if self.num_of_quantity == 1:
            Utils.pop(self, '1 item is the minimal', 'alert')
            return
        for child in self.color_size.children[:1]:
            self.color_size.remove_widget(child)
        if len(self.chosen_colors) == self.num_of_quantity:
            self.chosen_colors.pop(self.num_of_quantity)
        if len(self.chosen_sizes) == self.num_of_quantity:
            self.chosen_sizes.pop(self.num_of_quantity)
        self.num_of_quantity -= 1
        for off in self.user.active_buy_offers:
            a = 8
        self.set_total_price(None, None)

    def add_item(self):
        if self.num_of_quantity == 3:
            Utils.pop(self, '3 items is the max', 'alert')
            return
        if self.num_of_quantity > 0:
            if len(self.chosen_colors) != self.num_of_quantity:
                Utils.pop(self, 'have to chose color', 'alert')
                return
            if len(self.chosen_sizes) != self.num_of_quantity:
                Utils.pop(self, 'have to chose size', 'alert')
                return

        self.num_of_quantity += 1
        # BOX
        colors_sizes2 = BoxLayout(orientation='horizontal')
        colors_sizes2.size_hint_y = 0.1
        colors2 = BoxLayout(orientation='horizontal')
        sizes2 = BoxLayout(orientation='horizontal')
        colors_sizes2.add_widget(colors2)
        colors_sizes2.add_widget(sizes2)
        self.color_size.add_widget(colors_sizes2)
        # colors
        colors_counter = 0
        colors = self.offer.product.colors
        for color in colors:
            ip = "windows/images/colors/un_" + color + ".png"
            btn = MDIconButton(icon=ip)
            btn.text = color
            btn.bind(on_press=lambda item_number=self.num_of_quantity, color_chosen=color,
                                     item_number1=self.num_of_quantity, color_num=colors_counter: self.chose_color(
                item_number, color_chosen,
                item_number1, color_num)),
            colors2.add_widget(btn)
            colors_counter = colors_counter + 1

        # sizes
        sizes_counter = 0
        sizes = self.offer.product.sizes
        for size in sizes:
            btn = Button(text=size)
            btn.bind(on_press=lambda item_number=self.num_of_quantity, size11=size,
                                     item_number1=self.num_of_quantity, size_num=sizes_counter: self.chose_size(
                item_number, size11,
                item_number1, size_num))
            sizes2.add_widget(btn)
            sizes_counter = sizes_counter + 1

        self.set_total_price(None, None)

    def add_address(self):
        if hasattr(self, 'm'):
            self.m = Add_address(title='address', size_hint=(None, None), size=(400, 400))
            self.m.open()
        else:
            self.m = Add_address(title='address', size_hint=(None, None), size=(400, 400))
            self.m.open()

    def join_(self):
        # check buying details
        step = self.get_step()
        if step == -1:
            toast("you need to choose step ")
            return
        offer_id = self.offer_id
        quantity = self.num_of_quantity
        # check Validity Quantity Per Step
        if quantity > self.offer.steps[step].limit - self.offer.steps[step].buyers_amount:
            toast("there is not enough items for this step")
            return

        if len(self.chosen_colors) != self.num_of_quantity:
            toast("you have to choose color")
            return
        if len(self.chosen_sizes) != self.num_of_quantity:
            toast("you have to choose size")
            return

        colors = ""
        sizes = ""
        for color in self.chosen_colors:
            colors = colors + self.chosen_colors[color] + ','
        for size in self.chosen_sizes:
            sizes = sizes + self.chosen_sizes[size] + ','
        colors = colors[0:len(colors) - 1]
        sizes = sizes[0:len(sizes) - 1]

        # move to payment screen
        # self.PaymentScreen = PAYMENTScreen(offer_id, int(quantity), step, colors, sizes, self.new_address, self.user,
        #                                    self.offer).open()
        self.PaymentScreen = PAYMENTScreen(offer_id, int(quantity), step, colors, sizes, "new address s", self.user,
                                           self.offer).open()

    # end as a viewer

    def register(self):
        self.dismiss()
        a = App.get_running_app()
        a.root.current = 'connect_screen'
        Utils.pop("you need to register first", 'alert')

    def out(self):
        App.get_running_app().root.current = 'menu_screen'

    def dismiss(self):
        Popup.dismiss(self)

    def like_unlike(self):
        if self.user.is_a_liker(self.offer_id):
            self.controller.remove_liked_offer(self.offer_id)
            self.like.icon="windows/images/like.png"

        else:
            self.controller.add_liked_offer(self.offer_id)
            self.like.icon="windows/images/unlike.png"

    def add_item_for_update(self, colorz, sizez):
        self.num_of_quantity += 1

        # self.color_size = BoxLayout(orientation='horizontal')
        # self.box.add_widget(self.color_size)

        self.color_dropdown[self.num_of_quantity] = DropDown()
        colors = self.offer.product.colors
        for color in colors:
            btn = Button(text='%s' % color, size_hint=(None, None))
            btn.bind(on_release=lambda btn=self.num_of_quantity, color_chosen=btn.text,
                                       quant=self.num_of_quantity: self.save_color_first(btn, color_chosen, quant))
            self.color_dropdown[self.num_of_quantity].add_widget(btn)
        self.color_mainbutton[self.num_of_quantity] = Button(text=colorz)
        self.color_mainbutton[self.num_of_quantity].bind(on_release=self.color_dropdown[self.num_of_quantity].open)

        self.color_size.add_widget(self.color_mainbutton[self.num_of_quantity])
        self.color_dropdown[self.num_of_quantity].bind(on_select=lambda a=self.num_of_quantity,
                                                                        instance=self.color_mainbutton[
                                                                            self.num_of_quantity]: self.save_color_first(
            a, instance))

        # ------------------------------------------size-----------------

        self.size_dropdown[self.num_of_quantity] = DropDown()
        sizes = self.offer.product.sizes
        for size in sizes:
            btn = Button(text='%s' % size, size_hint=(None, None))
            btn.bind(on_release=lambda btn=self.num_of_quantity, size_chosen=btn.text,
                                       quant=self.num_of_quantity: self.save_size_first(btn, size_chosen, quant))
            self.size_dropdown[self.num_of_quantity].add_widget(btn)
        self.size_mainbutton[self.num_of_quantity] = Button(text=sizez)
        self.size_mainbutton[self.num_of_quantity].bind(on_release=self.size_dropdown[self.num_of_quantity].open)

        self.color_size.add_widget(self.size_mainbutton[self.num_of_quantity])
        self.size_dropdown[self.num_of_quantity].bind(on_select=lambda a=self.num_of_quantity,
                                                                       instance=self.size_mainbutton[
                                                                           self.num_of_quantity]: self.save_size_first(
            a, instance))

    def open_drop(self, a, num_of_quantity):
        self.color_dropdown[num_of_quantity].open

    def get_step(self):
        step = len(self.offer.steps)
        for checkbox in self.price_per_step.children:
            if type(checkbox) is MDCheckbox:
                if checkbox.active:
                    return step
                step -= 1
        return -1

    def update_purchase(self):
        sizez = ",".join(self.chosen_sizes.values())
        colorz = ",".join(self.chosen_colors.values())
        print(str(self.chosen_sizes.values()))
        print(type(str(self.chosen_sizes.values())))
        step = len(self.offer.steps)
        # self.controller.remove_active_buy_offer(self.offer_id)
        step = self.get_step()
        if step == -1:
            toast("you need to choose step ")
            return
        offer_id = self.offer_id
        quantity = self.num_of_quantity
        ans = self.controller.update_active_buy_offer(self.offer_id, quantity, step, colorz, sizez,
                                                      self.purchase.address)
        if ans.res is True:
            for item in self.user.active_buy_offers:
                if item.offer_id == self.offer_id:
                    self.user.active_buy_offers.remove(item)
            self.user.get_active_buy_offers().append(self.offer)
            self.offer = ans.data
            data = App.get_running_app().root.current_screen.ids.Main_page_box.children[1].data
            for object in data:
                offer = object['offer']
                if offer[0].offer_id == self.offer_id:
                    a = ans.data.current_buyers
                    to_return = {}
                    for buyer in ans.data.current_buyers:
                        to_return[buyer['buyer_id']] = Struct(**buyer)
                    offer[0].current_buyers = to_return
            self.dismiss()
            return

    def cancel_purchase(self):
        ans = self.controller.remove_active_buy_offer(self.offer_id)
        if ans.res is True:
            # self.user.get_active_buy_offers().append(self.offer)
            cc = self.user.get_active_buy_offers()
            self.offer = ans.data
            for offerz in self.user.active_buy_offers:
                if offerz.offer_id == self.offer_id:
                    self.user.active_buy_offers.remove(offerz)
            data = App.get_running_app().root.current_screen.ids.Main_page_box.children[1].data
            for object in data:
                offer = object['offer']
                if offer[0].offer_id == self.offer_id:
                    a = ans.data.current_buyers
                    to_return = {}
                    for buyer in ans.data.current_buyers:
                        to_return[buyer['buyer_id']] = Struct(**buyer)
                    offer[0].current_buyers = to_return
            # self.user.active_buy_offers.remove(ans.data)
        self.dismiss()

    def remove_offer(self):
        self.dismiss()
        ans = self.controller.remove_active_sell_offer(self.offer_id)
        if ans.res is True:
            pass

    def update_offer(self):
        self.dismiss()
        App.get_running_app().root.current = 'update_offer'
        c = App.get_running_app().root
        e = App.get_running_app().root.screens
        f = App.get_running_app().root.screens[6]
        c = self.offer
        f = App.get_running_app().root.screens[6].update_offer(self.offer)

    def split_list(self, lis):
        x = lis.split(',')
        return x[:-1]

    def split_str(self, str):
        to_return = str.split(',')
        if to_return[-1] == '':
            to_return = to_return[:-1]
        return to_return

    def list_to_dict(self, lis):
        i = 1
        dict = {}
        for val in lis:
            dict[i] = val
            i += 1
        return dict

    def insert_photos(self, car, photos):
        for photo in photos:
            if photo is not None:
                image = photo
                data = io.BytesIO(image)
                data.seek(0)
                img = CoreImage(data, ext="png").texture

                new_img = Image()
                new_img.texture = img
                new_img.allow_stretch = True
                car.add_widget(new_img)


class Add_address(Popup):
    def __init__(self, **kwargs):
        super(Add_address, self).__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.address = MDTextField(hint_text='ADDRESS')
        self.box.add_widget(self.address)
        self.insert = Button(text="INSERT")
        self.insert.bind(on_press=lambda x: self.insert_add())
        self.box.add_widget(self.insert)
        self.back = Button(text="BACK")
        self.back.bind(on_press=lambda x: self.out())
        self.box.add_widget(self.back)
        self.add_widget(self.box)

    def out(self):
        self.dismiss()

    def insert_add(self):
        self.parent.children[1].new_address = self.address.text
        self.parent.children[1].other_address.text = self.address.text
        self.parent.children[1].change = True
        self.dismiss()
