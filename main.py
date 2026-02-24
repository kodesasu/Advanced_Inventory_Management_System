from collections import namedtuple, defaultdict, Counter
from logging.handlers import RotatingFileHandler
import os, logging

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ProductInventoryLogs.log")
log_handler = RotatingFileHandler(
    file_path,
    maxBytes=5*1024*1024,
    backupCount=3,
    encoding="utf-8"
)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.basicConfig(level=logging.DEBUG,
                    handlers=[log_handler])


class DataLayer:
    def __init__(self):
        self.Product = namedtuple(
            "Product", [
                "ID", "name",
                "company", "category",
                "sub_category", "price",
                "stock"
            ]
        )

        self.products = {}
        self.products_names = set()
        self.category = defaultdict(list)
        self.sub_category = defaultdict(list)
        self.company = defaultdict(list)
        self.all_search_fields = {
            "Company": self.company,
            "Category": self.category,
            "Sub-Category": self.sub_category
        }


    def add_product(self, product_data):
        new_product = self.Product(product_data["ID"], product_data["name"],
                              product_data["company"], product_data["category"],
                              product_data["sub_category"], product_data["price"],
                              product_data["stock"])
        self.products[new_product.ID] = new_product
        self.products_names.add(new_product.name)
        self.company[new_product.company].append(new_product.ID)
        self.category[new_product.category].append(new_product.ID)
        self.sub_category[new_product.sub_category].append(new_product.ID)
        logging.info(f"Product Added successfully [ID: {new_product.ID} | Name: {new_product.name}]\n")


    def get_product(self):
        logging.debug("Returning Product Dictionary (self.products)")
        return self.products


class ValidationLayer:
    def positive_integer(self, value):
        logging.info("Checking for Positive integer")
        if len(value.strip()) == 0:
            logging.warning("Input is empty | Returning")
            return False, "Input cannot be empty"

        if not value.isdigit():
            logging.warning("Input is not an integer| Returning")
            return False, "Input must be an integer"

        logging.info("Input is an integer| Returning Input")
        return True, int(value)

    def positive_number(self, value):
        logging.info("Checking for Positive number")
        value_state = False
        try_value = None

        if len(value.strip()) == 0:
            logging.warning("Input is empty | Returning")
            return value_state, "Input cannot be empty"
        try:
            value = float(value)

            if value < 0:
                logging.warning("Input is not an positive number| Returning")
                try_value = "Input must be a positive number"
            else:
                value_state = True
                logging.info("Input is a positive number| Returning Input")
                try_value = round(value, 4)

        except ValueError:
            logging.warning("Input is not an positive number| Returning")
            try_value = "Input must be a number"
        return value_state, try_value


    def string_non_empty(self, value):
        logging.debug("Checking for Empty Input")
        if len(value.strip()) == 0:
            logging.warning("Input is empty | Returning")
            return False, "Input cannot be empty"
        logging.info("Input is not empty | Returning")
        return True, value.strip().capitalize()

class OperationLayer:
    def __init__(self, data_layer=None):
        self.dl = data_layer if data_layer else DataLayer()
        self.vl = ValidationLayer()
        self.product_db = {}

    def check_validity(self, data, validation):
        logging.debug(f"Passing Data for Validation")
        return validation(data)

    def create_id(self, product_data, counter):
        p_name, p_category, p_subcategory = product_data[0], product_data[2], product_data[3]
        no = counter
        i_d = f"{no:04}{p_name[0]}{p_category[0]}{p_subcategory[0]}"
        logging.info(f"ID created successfully[{i_d}]\n")
        return i_d

    def create_product_db(self, product_list):
        self.product_db["name"] = product_list[0]
        self.product_db["company"] = product_list[1]
        self.product_db["category"] = product_list[2].capitalize()
        self.product_db["sub_category"] = product_list[3].capitalize()
        self.product_db["price"] = product_list[4]
        self.product_db["stock"] = product_list[5]
        self.product_db["ID"] = product_list[6]
        self.dl.add_product(self.product_db)
        logging.info(f"Product[{self.product_db["name"]}] has been registered in database | Passing to Inventory")
        return self.product_db

    def check_id(self, i_d):
        logging.debug("Checking for duplicate ID")
        return i_d in self.dl.products

    def check_name(self, p_name):
        logging.debug("Checking for duplicate names")
        return any(p_name == name for name in self.dl.products_names)

    def search_data(self, p_data):
        matching_ids = set()
        logging.info(f"Searching data [{p_data}] in Inventory")
        for search_term in [p_data.upper(), p_data.capitalize()]:
            if search_term in self.dl.company:
                logging.debug(f"[{p_data}] Found in Product Company")
                matching_ids.update(self.dl.company[search_term])

            if search_term in self.dl.category:
                logging.debug(f"[{p_data}] Found in Product Category")
                matching_ids.update(self.dl.category[search_term])

            if search_term in self.dl.sub_category:
                logging.debug(f"[{p_data}] Found in Product Sub-category")
                matching_ids.update(self.dl.sub_category[search_term])

            for product_id, product in self.dl.products.items():
                if search_term in product.name:
                    logging.debug(f"[{p_data}] Found in Product Names")
                    matching_ids.add(product_id)

        selected_products = [self.dl.products[p_id] for p_id in matching_ids]
        logging.info("Returning Results\n")
        return selected_products if selected_products else None

    def check_empty_product(self):
        logging.info("Returning Product Inventory")
        return self.dl.get_product()

    def get_all_search(self):
        logging.info("Returning Product Fields\n")
        return self.dl.all_search_fields

    def add_product(self, product_data):
        logging.debug(f"Product data Successfully added to inventory\n")
        self.dl.add_product(product_data)
        return "Product Added Successfully"

    def add_stocks(self, stock_a, key, product):
        stock_amount = int(stock_a)
        logging.debug("Replacing old stock with new stock")
        updated_product = product._replace(stock=product.stock + stock_amount)
        self.dl.products[key] = updated_product
        logging.info("Operation successful| Returning\n")
        return  self.dl.products[key].stock

    def inventory_analysis(self):
        if not self.dl.products:
            return
        logging.info("Loading Inventory Analysis")
        count_category = Counter(v.category for v in self.dl.products.values())
        count_sub_category = Counter(v.sub_category for v in self.dl.products.values())
        count_company = Counter(v.company for v in self.dl.products.values())
        count_low_stocks = sum(1 if p.stock < 10 else 0 for p in self.dl.products.values())
        count_low_stocks_full = {p.name : p.stock for p in self.dl.products.values() if p.stock < 10}
        total_stocks_per_category = {}

        for v in self.dl.products.values():
            total_stocks_per_category[v.category] = total_stocks_per_category.get(v.category, 0) + v.stock
        avg_stocks_per_category = {k: total_stocks_per_category[k]/count_category[k] for  k in count_category.keys()}
        logging.info("Analysis complete | Returning analysis")
        return (count_category, count_sub_category, count_company, count_low_stocks, count_low_stocks_full,
                avg_stocks_per_category)


class UserInterfaceLayer:
    def __init__(self, operation_layer=None):
        self.ol = operation_layer if operation_layer else OperationLayer(data_layer=DataLayer())
        self.vl = ValidationLayer()

    def display_summary(self, heading, data):
        print(f"Product Count by {heading}")
        for k, v  in data.items():
            print(f"{k} | Count: {v}")
        print()

    def display_summary_analysis(self):
        logging.debug("Trying to get Analysis")
        all_analysis = self.ol.inventory_analysis()
        if not all_analysis:
            logging.error("Operation Failed | No products in Inventory | Returning\n")
            print('No products Available for Analysis | Try adding a Product')
            print()
            return
        (count_category, count_sub_category, count_company, count_low_stocks, count_low_stocks_full,
         avg_stocks_per_category) = all_analysis

        logging.info("Displaying Analysis\n")
        print(f"{'=' * 7} SUMMARY ANALYSIS {'=' * 7}")
        self.display_summary("Category", count_category)
        self.display_summary("Sub-Category", count_sub_category)
        self.display_summary("Company", count_company)
        self.display_summary("Average Stocks Per Category", avg_stocks_per_category)
        if count_low_stocks < 1:
            return

        print(f"Low Stocks(Below 10) are: {count_low_stocks}\nWould you like to see all Products with low stocks:")
        logging.debug("Waiting for user choice on: see all Products with low stocks")
        option = self.option_conflict_list([("A", "Yes"), ("B", "No")])
        if option == "B":
            logging.info("User selected: No | Returning")
            print()
            return

        logging.info("User selected: Yes | Showing All Low stocks products\n")
        self.display_summary("Low Stocks", count_low_stocks_full)



    def update_stocks(self, p_name):
        c_key, c_product = None, None
        logging.debug("Trying to: Update Stocks")
        for key, value in self.ol.check_empty_product().items():
            if p_name == value.name:
                c_key, c_product = key, value

        stock_amount = f"Current stock[{c_product.stock}]\nEnter amount to add: "
        logging.info("Checking User Input for Errors")
        stock = self.error_looper(stock_amount, self.vl.positive_integer)
        if not stock:
            logging.warning("User Decided to stop the process| Returning\n")
            return
        logging.info("No Errors Found")
        new_stock = self.ol.add_stocks(stock, c_key, c_product)
        logging.info("Stocks Updated Successfully")
        print(f"Stock Added successfully\nNew stock for {p_name}: {new_stock}")

    def option_conflict_list(self, options):
        count = 1
        option_list = []

        logging.debug("Displaying options| Version(list)")
        for i in options:
            option_list.append(i[0])
            print(f"[{i[0]}] {i[1]}")
        choice = input("Select an option: ").strip().upper()
        logging.info("Waiting for User input")

        while choice not in option_list:
            logging.info(f"User input not in Options| retry: {count}")
            if choice.lower() == "q":
                logging.warning("User selected 'q' to break the process| Returning\n")
                return None
            if count >= 2:
                print("Enter 'q' to go back")
                print()
                print("These are your options")
                for i in options:
                    print(f"[{i[0]}] {i[1]}")

            count += 1
            choice = input("Select a valid option: ").strip().upper()
            print(f"You entered : {choice}")
        logging.debug("Returning User Input")
        return choice

    def option_conflict_dict(self, options):
        count = 1
        logging.debug("Displaying options| Version(Dict)")
        while True:
            for k, v in options.items():
                print(f"[{k}] {v}")
            choice = input("Select an option: ").strip().upper()
            if choice.lower() == "q":
                logging.warning("User selected 'q' to break the process| Returning\n")
                return None
            if count > 2:
                print("Enter 'q' to go back")
                print()

            if options.get(choice):
                logging.debug("Returning User Input\n")
                return options.get(choice)

            logging.info(f"User input not in Options| retry: {count}")
            print(f"You entered : {choice}")
            print("These are your options")
            count += 1

    def name_sorter(self, name):
        logging.debug("Trying to Sort Name Conflict")
        selection_list = [("A", "Add stocks"),
                          ("B", "Use name(Different ID)"),
                          ("C", "Go Back")
                          ]
        print("\nName already exist\nWhat should be done: ")
        choice = self.option_conflict_list(selection_list)
        if choice == "A":
            logging.info("User Decided to: Add stocks\n")
            self.update_stocks(name)
            print()
            return None

        elif choice == "B":
            logging.info("User Decided to: Use name(Different ID)\nn")
            print()
            return name
        else:
            logging.info("User Decided to: Go Back\n")
            return None

    def error_looper(self, data, validation):
        count = 1
        logging.debug("Trying to check for errors")
        while True:
            collect = input(data)

            if collect.lower() == "q":
                logging.warning("User selected 'q' to break the process| Returning\n")
                return None
            logging.debug("Trying to Validate user input")
            is_valid, info = self.ol.check_validity(collect.strip(), validation)

            if is_valid:
                logging.info("No errors found| Returning Data\n")
                return info
            else:
                logging.error(f"Error Found: {info}")
                print(info)

            if count > 2:
                print("Enter 'q' to go back")
                print()
            count += 1


    def add_product_menu(self):
        logging.debug("Trying to register a product")
        product_db = []
        input_list = ["Enter company name: ", "Enter category name(Electronics, Food,...): ",
                      "Enter sub_category(Electronics(laptop, phone,...), Food(grain,...)): "
                      ]
        log_field_list = [k for k in self.ol.get_all_search().keys()]

        count = 1
        print(f"\n{'=' * 7} REGISTERING PRODUCT {'=' * 7}")
        logging.debug("Checking for Errors in Product Name")
        product_name = self.error_looper("Enter product name: ", self.vl.string_non_empty)
        if not product_name:
            logging.warning("User decided to break the process| Returning\n")
            return None
        logging.debug("Checking for Uniqueness in Product Name")
        is_valid = self.ol.check_name(product_name.capitalize())

        if not is_valid:
            logging.info("Product name is Unique| Name Registered\n")
            product_db.append(product_name.capitalize())

        else:
            logging.warning("Product name is not Unique| Developing solutions")
            is_name_valid = self.name_sorter(product_name.capitalize())
            if not is_name_valid:
                logging.warning("User decided to break the process| Returning\n")
                return None
            logging.info("Solution Developed| Name Registered\n")
            product_db.append(is_name_valid.capitalize())

        for index, i in enumerate(input_list):
            logging.debug(f"Checking for Errors in Product {log_field_list[index]}")
            value = self.error_looper(i, self.vl.string_non_empty)
            if value:
                logging.info(f"Product {log_field_list[index]} Registered successfully\n")
                product_db.append(value)

            else:
                logging.warning("User decided to break the process| Returning\n")
                return None


        logging.debug("Checking for Errors in Product Price")
        price = self.error_looper("Enter product price: ", self.vl.positive_number)
        if not price:
            logging.warning("User decided to break the process| Returning\n")
            return None
        logging.info("Product Price registered successfully\n")
        product_db.append(price)

        logging.debug("Checking for Errors in Product Stock")
        stock = self.error_looper("Enter product stock: ", self.vl.positive_integer)
        if not stock:
            logging.warning("User decided to break the process| Returning\n")
            return None
        logging.info("Product Stock registered successfully\n")
        product_db.append(stock)

        logging.debug("Trying to create ID")
        i_d = self.ol.create_id(product_db, count)

        logging.info("ID created | Checking for Uniqueness")
        while self.ol.check_id(i_d):
            count += 1
            i_d = self.ol.create_id(product_db, count)
        logging.info("ID registered Successfully")
        product_db.append(i_d)
        main_db = self.ol.create_product_db(product_db)
        logging.info("All Product Database Fields Registered Successfully| Returning Product Database\n")
        return main_db

    def display_product_menu(self):
        selection_list = [("A", "Display only Product IDs"),
                          ("B", "Display full Product Info"),
                          ("C", "Go Back")
                          ]
        logging.debug("Trying to: Display Product")
        products = self.ol.check_empty_product()
        if not products:
            logging.error("No products in inventory| Returning\n")
            print("No products Available | Try adding a Product")
            return
        print(f"\n{'=' * 7} DISPLAYING PRODUCT(S) {'=' * 7}")
        print("How do you want to display it: ")
        choice = self.option_conflict_list(selection_list)
        if choice == "A":
            logging.info("User decided to display all products by IDs\n")
            print(f"{'=' * 7} Product By IDs {'=' * 7}")
            for index, k in enumerate(products.keys(), start=1):
                print(f"[{index}] {k}")

        elif choice == "B":
            logging.info("User decided to display all product full Information\n")
            print(f"{'=' * 7} ALL PRODUCTS {'=' * 7}")
            for index, (i_d, product) in enumerate(products.items(), start=1):
                print(f"[{index}] Name: {product.name}, ID: {i_d} | [Company: {product.company}, "
                      f"Category: {product.category}, "
                      f"Sub-Category: {product.sub_category}, "
                      f"Price: ${product.price:.2f}, "
                      f"Stock: {product.stock}]")
        else:
            logging.warning("User decided to break the process| Returning\n")
            return

    def search_product(self, products):
        logging.debug("Trying to: Search Product (Advance Search)")
        search_field_options = {chr(ord("A") + i): k for i, k in enumerate(self.ol.get_all_search().keys())}
        print(f"\n{'=' * 7} ADVANCED SEARCH {'=' * 7}")
        print("Search By:")
        logging.debug("Getting Product filed option")
        selected_field_option = self.option_conflict_dict(search_field_options)

        if not selected_field_option:
            logging.warning("User decided to break the process| Returning\n")
            return None

        logging.info(f"User selected [{selected_field_option}]| getting sub-fields")
        selected_field = self.ol.get_all_search()[selected_field_option]
        search_subfield_options = {chr(ord("A") + i): k for i, k in
                                   enumerate(selected_field.keys())}
        print(f"\n{'=' * 7} Searching in {selected_field_option} {'=' * 7}")
        print(f"Enter specific {selected_field_option} :")
        selected_option = self.option_conflict_dict(search_subfield_options)

        if not selected_option:
            logging.warning("User decided to break the process| Returning\n")
            return None

        logging.info(f"User selected [{selected_option}]| getting IDs")
        selected_option_id = selected_field[selected_option]
        search_product = [v for k, v in products.items() if k in selected_option_id]
        logging.info("Returning Searched Products\n")
        return selected_option, search_product

    def filtered_price(self, products):
        logging.debug("Trying to: Filter Search by Price")
        logging.debug("Checking for errors in User Input")
        filter_no = self.error_looper("Enter a Price: ", self.vl.positive_number)
        if not filter_no:
            logging.warning("User decided to break the process| Returning\n")
            return None, ""

        logging.info("No Errors| waiting for User on Decision")
        numlist = [("A", f"Price above ${filter_no:.2f}"), ("B", f"price below ${filter_no:.2f}")]
        selected_range = self.option_conflict_list(numlist)

        if not selected_range:
            logging.warning("User decided to break the process| Returning\n")
            return None, ""

        if selected_range == "A":
            logging.info(f"User Decided to Filter Price above ${filter_no:.2f}\n")
            filter_product = [v for v in products if v.price >= round(float(filter_no), 4)]
            return (filter_product, numlist[0][1]) if filter_product else (None,
                                                                           f"No Available products with {numlist[0][1]}")
        else:
            logging.info(f"User Decided to Filter Price below ${filter_no:.2f}\n")
            filter_product = [v for v in products if v.price <= round(float(filter_no), 4)]
            return filter_product, numlist[1][1] if filter_product else (None,
                                                                           f"No Available products with {numlist[1][1]}")

    def filtered_stock(self, products):
        logging.debug("Trying to: Filter Search by Stock")
        logging.debug("Checking for errors in User Input")
        filter_no = self.error_looper("Enter a number: ", self.vl.positive_integer)
        if not filter_no:
            logging.warning("User decided to break the process| Returning\n")
            return None, ""

        logging.info("No Errors| waiting for User on Decision")
        numlist = [("A", f"Stock above {filter_no} item(s)"), ("B", f"Stock below {filter_no} item(s)")]
        selected_range = self.option_conflict_list(numlist)

        if not selected_range:
            logging.warning("User decided to break the process| Returning\n")
            return None, ""

        if selected_range == "A":
            logging.info(f"User Decided to Filter Stock above ${filter_no:.2f}\n")
            filter_product = [v for v in products if v.stock >= int(filter_no)]
            return filter_product, numlist[0][1] if filter_product else (None,
                                                                           f"No Available products with {numlist[0][1]}")
        else:
            logging.info(f"User Decided to Filter Stock below ${filter_no:.2f}\n")
            filter_product = [v for v in products if v.stock <= int(filter_no)]
            return filter_product, numlist[1][1] if filter_product else (None,
                                                                           f"No Available products with {numlist[1][1]}")



    def filtered_search(self, products):
        logging.debug("Trying to: Filter Product")
        category = {chr(ord("A") + i) : j for i, j in enumerate({v.category for v in products})}
        sub_category = {chr(ord("A") + i): j for i, j in enumerate({v.sub_category for v in products})}
        company = {chr(ord("A") + i): j for i, j in enumerate({v.company for v in products})}
        filter_list = [(chr(ord("A") + i), k) for i, k in enumerate(self.ol.get_all_search().keys())]
        price_op, stock_op, go_back = (chr(ord(filter_list[len(filter_list) - 1][0]) + 1),
                                       chr(ord(filter_list[len(filter_list) - 1][0]) + 2),
                                       chr(ord(filter_list[len(filter_list) - 1][0]) + 3))

        filter_list.extend([(price_op, "Price"), (stock_op, "Stock"), (go_back, "Go Back")])
        print(f"\n{'=' * 7} FILTER PRODUCTS {'=' * 7}")
        print("Filter by: ")
        logging.info("Waiting on user decision")
        selected_option = self.option_conflict_list(filter_list)
        if not selected_option or selected_option == go_back:
            logging.warning("User decided to break the process| Returning\n")
            print()
            return None

        elif selected_option == price_op:
            logging.info("User Decided to filter: By price")
            is_empty, data = self.filtered_price(products)
            if not is_empty:
                print(data)
                return None
            else:
                return is_empty, data

        elif selected_option == stock_op:
            logging.info("User Decided to filter: By Stock")
            is_empty, data = self.filtered_stock(products)
            if not is_empty:
                print(data)
                return None
            else:
                return is_empty, data

        elif selected_option == "A":
            logging.info("User Decided to filter: By Category")
            selected_category = self.option_conflict_dict(category)
            if not selected_category:
                return None

            filter_product = [v for v in products if selected_category == v.category]
            return filter_product, selected_category

        elif selected_option == "B":
            logging.info("User Decided to filter: By Sub-category")
            selected_category = self.option_conflict_dict(sub_category)
            if not selected_category:
                return None

            filter_product = [v for v in products if selected_category == v.sub_category]
            return filter_product, selected_category

        else:
            logging.info("User Decided to filter: By Company")
            selected_category = self.option_conflict_dict(company)
            if not selected_category:
                return None

            filter_product = [v for v in products if selected_category == v.company]
            return filter_product, selected_category




    def single_search_by_keyword(self):
        count = 1
        logging.debug("Trying to: Search Product(Quick search)")
        print(f"{'=' * 7} QUICK SEARCH {'=' * 7}")
        while True:
            search_term = self.error_looper("Enter what you want to search for: ", self.vl.string_non_empty)
            if not search_term:
                return None

            selected_products = self.ol.search_data(search_term)

            if selected_products:
                logging.info("Products found|returning Found products")
                return search_term, selected_products

            logging.info(f"No products found| retry[{count}]")
            print("No products found")
            if count > 2:
                print("Enter 'q' to go back")
                print()
            count += 1



    def search_options(self):
        logging.debug("Trying to: Search in product inventory")
        products = self.ol.check_empty_product()

        if not products:
            logging.error("No Products Available| Returning\n")
            print("No products Available | Try adding a Product")
            return
        logging.info("Waiting on User Decision for search options")

        search_options = [("A", "Quick Search"), ("B", "Advanced Search")]
        filter_choice = [("A", "Yes"), ("B", "No")]
        print(f"\n{'=' * 7} SEARCH PRODUCT(S) {'=' * 7}")
        print("Enter search option: ")
        selected_option = self.option_conflict_list(search_options)
        print()
        if not selected_option:
            logging.error("User decided to break the process| Returning\n")
            return

        if selected_option == "A":
            logging.info("User decided: Quick Search")
            data = self.single_search_by_keyword()
            if not data:
                return

            field, searched_products = data
            print(f"{len(searched_products)} Product(s) Found")

            logging.info("Displaying Searched Products")
            print(f"These are the product(s) associated with {field}")
            for index, product in enumerate(searched_products, start=1):
                print(f"[{index}] Name: {product.name} | [Company: {product.company}, "
                      f"Category: {product.category}, Sub-Category: {product.sub_category}, "
                      f"Price: ${product.price:.2f}, Stock: {product.stock}]")
            print()
            count = 1

            logging.info("Waiting on User Decision for filter options")
            while True:
                if count > 1:

                    print("would you like to filter products again: ")
                else:
                    print("would you like to filter products: ")
                selected_filter_choice = self.option_conflict_list(filter_choice)

                if not selected_filter_choice or selected_filter_choice == "B":
                    logging.warning("User decided to break the process| Returning\n")
                    return

                new_data = self.filtered_search(searched_products)
                if new_data:
                    count += 1
                    filtered_products, filtered_choice = new_data

                    logging.info("Displaying Filtered Products")
                    print(f"{len(filtered_products)} Product(s) filtered by {filtered_choice}")
                    for index, product in enumerate(filtered_products, start=1):
                        print(f"[{index}] Name: {product.name} | [Price: ${product.price:.2f}, Stock: {product.stock}]")
                    print()



        else:
            logging.info("User decided: Advanced Search")
            data = self.search_product(products)
            print()
            if not data:
                return

            field, searched_products = data
            logging.info("Displaying Searched Products")
            print(f"These are the products in {field}")
            for index, product in enumerate(searched_products, start=1):
                print(f"[{index}] Name: {product.name} | [Price: ${product.price:.2f}, Stock: {product.stock}]")
            print()

            count = 1
            logging.info("Waiting on User Decision for filter options")
            while True:
                filter_digits_list = [("A", "Price"), ("B", "Stock")]
                print(f"\n{'=' * 7} FILTER PRODUCTS {'=' * 7}")
                if count > 1:
                    print("would you like to filter products again: ")
                else:
                    print("would you like to filter products: ")
                selected_filter_choice = self.option_conflict_list(filter_choice)

                if not selected_filter_choice or selected_filter_choice == "B":
                    logging.warning("User decided to break the process| Returning\n")
                    return
                count += 1
                print("Filter By:")
                selected_filter_digits = self.option_conflict_list(filter_digits_list)
                if not selected_filter_digits:
                    return

                if selected_filter_digits == "A":
                    logging.info("User decided to filter by Price")
                    filtered_products, filtered_choice = self.filtered_price(searched_products)
                    count += 1
                    if not filtered_products:
                       print(filtered_choice)
                       print()
                    else:
                        logging.debug("Displaying Filter By Price")
                        print(f"{len(filtered_products)} Product(s) filtered by {filtered_choice}")
                        for index, product in enumerate(filtered_products, start=1):
                            print(
                                f"[{index}] Name: {product.name} | [Price: ${product.price:.2f}, "
                                f"Stock: {product.stock}]")
                        print()
                else:
                    logging.info("User decided to filter by Stock")
                    filtered_products, filtered_choice = self.filtered_stock(searched_products)
                    count += 1
                    if not filtered_products:
                        print(filtered_choice)
                        print()
                    else:
                        logging.debug("Displaying Filter By Price")
                        print(f"{len(filtered_products)} Product(s) filtered by {filtered_choice}")
                        for index, product in enumerate(filtered_products, start=1):
                            print(
                                f"[{index}] Name: {product.name} | [Price: ${product.price:.2f}, "
                                f"Stock: {product.stock}]")
                        print()






    def run_program(self):
        logging.info("\nStarting Programme\n")
        options = [("A", "Add Product"),
                   ("B", "Display Products"),
                   ("C", "Search Products"),
                   ("D", "Display Product Analysis"),
                   ("E", "Quit")
                   ]
        print(f"{'=' * 7} Advanced Inventory Management System {'=' * 7}")
        while True:
            print("What would you like to do")
            logging.debug("Waiting on User Decision")

            for i in options:
                print(f"[{i[0]}] {i[1]}")
            choice = input("Select an option: ").strip().upper()
            if choice == "E":
                logging.info("User Decided to Quit\nProgramme Ended\n")
                print("Goodbye!!!")
                return

            elif choice == "A":
                logging.info("User Decided to: Add a Product")
                data = self.add_product_menu()
                if data:
                    print(f"Product Added successfully\nYour ID is:[{data["ID"]}]")
                    print()

            elif choice == "B":
                logging.info("User Decided to: Display Products")
                self.display_product_menu()
                print()

            elif choice == "C":
                logging.info("User Decided to: Search Products")
                self.search_options()
                print()
            elif choice == "D":
                logging.info("User Decided to: Request for Analysis")
                self.display_summary_analysis()

            else:
                logging.info("User Entered an Invalid Input\n")
                print("Invalid Input")


if __name__ == "__main__":
    ui = UserInterfaceLayer(operation_layer=OperationLayer())
    ui.run_program()













