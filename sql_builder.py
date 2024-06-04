from constants import *

def write_sql_commands(sql_commands, output_file):
    with open(output_file, 'w') as file:
        for command in sql_commands:
            file.write(command + '\n')

def create_settings_sql():
    settings_sql = ["-- Use this SQL to completely cleanse the map database. The result will be as if the database had been created again"\
    "\nTRUNCATE TABLE Location, Menu, Menugroup, Tag, Link, Links_group, Tag_related_locations, Tag_relationship;"\
    "\n\nalter sequence administration_location_id_seq restart with 1;"\
    "\nalter sequence administration_menu_id_seq restart with 1;"\
    "\nalter sequence menugroup_id_seq restart with 1;"
    "\nalter sequence administration_tag_id_seq restart with 1;"\
    "\nalter sequence administration_tag_related_locations_id_seq restart with 1;"\
    "\nalter sequence administration_tag_relationship_id_seq restart with 1;"\
    "\n\n-- Setting map settings for Pontos de coleta"\
    f"\nUPDATE map_config SET map_name = '{MAP_NAME}';"\
    f"\nUPDATE map_config SET initial_zoom_level = {INITIAL_ZOOM_LEVEL};"\
    f"\nUPDATE map_config SET initial_latitude = {INITIAL_LATITUDE};"\
    f"\nUPDATE map_config SET initial_longitude = {INITIAL_LONGITUDE};\n\n"]

    return settings_sql

def create_menus_group_sql(menus_group):
    menus_group_sql = []
    menus_group_sql.append("-- Inserting Menus Group")

    for menu_group in menus_group.values():
        menus_group_sql.append(f"INSERT INTO MenuGroup (id,name) VALUES" \
                                f"('{menu_group['menu_group_id']}','{menu_group['name']}');")
    
    menus_group_sql.append(f"\nalter sequence menugroup_id_seq restart with {len(menus_group)};\n\n")

    return menus_group_sql

def create_menus_sql(menus):
    menus_sql = []
    menus_sql.append("-- Inserting Menus")

    # latest_menus = {}

    # Ordena os menus por ordem alfabetica
    sorted_menus = dict(sorted(menus.items(), key=lambda item: item[1]["name"]))

    for menu_key, menu in sorted_menus.items():
        menus_sql.append(f"INSERT INTO Menu (id,name,group_id,hierarchy_level,active) VALUES" \
                            f"('{menu['menu_id']}','{menu['name']}', '{menu['menu_group_id']}', '{menu['hierarchy_level']}', {menu['active']});")
    
    menus_sql.append(f"\nalter sequence administration_menu_id_seq restart with {len(menus)};\n\n")
    return menus_sql

def create_locations_sql(locations):
    locations_sql = []
    locations_sql.append("-- Inserting Locations")

    for location in locations.values():
        locations_sql.append(f"INSERT INTO Location (id, name, description, overlayed_popup_content, latitude, longitude, active) VALUES " \
                        f"('{location['location_id']}', '{location['name']}', '{location['description']}', '{location['overlayed_popup_content']}', '{location['latitude']}', '{location['longitude']}', {location['active']});")

    
    locations_sql.append(f"\nalter sequence administration_location_id_seq restart with {len(locations)};\n\n")
    return locations_sql

def create_tags_sql(tags):
    tags_sql = []
    tags_sql.append(f"-- Inserting Tags")

    for tag in tags.values():
        tags_sql.append(f"INSERT INTO Tag (id,name,description,color,active,parent_menu_id) VALUES " \
                            f"('{tag['tag_id']}', '{tag['name']}', '{tag['description']}', '{tag['color']}', {tag['active']}, '{tag['parent_menu_id']}');")

    tags_sql.append(f"\nalter sequence administration_tag_id_seq restart with {len(tags)};\n\n")

    return tags_sql

def create_tags_related_locations_sql(tags_related_locations):
    tags_related_locations_sql = []

    tags_related_locations_sql.append(f"-- Tags relationship with Locations")

    for tag_related_location in tags_related_locations.values():
        tags_related_locations_sql.append(f"INSERT INTO Tag_related_locations (id, tag_id, location_id) VALUES " \
                                    f"('{tag_related_location['tags_related_locations_id']}', '{tag_related_location['tag_id']}', '{tag_related_location['location_id']}');")

    tags_related_locations_sql.append(f"\nalter sequence administration_tag_related_locations_id_seq restart with {len(tags_related_locations)};\n\n")

    return tags_related_locations_sql

def create_all_sql_commands(menus_group, menus, locations, tags, tags_related_locations):
    sql_commands = []

    # #Configurações iniciais do mapa
    sql_commands.extend(create_settings_sql())

    sql_commands.extend(create_menus_group_sql(menus_group))
    sql_commands.extend(create_menus_sql(menus))
    sql_commands.extend(create_locations_sql(locations))
    sql_commands.extend(create_tags_sql(tags))
    sql_commands.extend(create_tags_related_locations_sql(tags_related_locations))
    
    return sql_commands