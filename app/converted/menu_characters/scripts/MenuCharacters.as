package
{
    public dynamic class MenuCharacters extends SSF2Asset
    {

        public function MenuCharacters():void
        {
            super();
            register("id", "menu_characters");
            register("guid", "cdf5fc26-48fa-4f20-9279-e01e4cea0fe2");
            register("resources", {
                "movieclips":["blankmc2", "menu_charselect_arena", "menu_charselect_classic", "menu_charselect_crystal", "menu_charselect_event", "menu_charselect_hrc", "menu_charselect_multiman", "menu_charselect_online", "menu_charselect_targettest", "menu_charselect_training", "menu_charselect_vs", "CharacterSelectBox", "CharacterSelectChip"],
                "sounds":[]
            });
        }

    }
}

