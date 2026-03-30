package menu_characters_fla
{
    import flash.display.MovieClip;

    public dynamic class FreeForAllHighlight_7 extends MovieClip
    {

        public var gameModeTxt:MovieClip;

        public function FreeForAllHighlight_7()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3);
        }

        internal function frame1():*
        {
            this.buttonMode = true;
            this.mouseChildren = false;
            stop();
        }

        internal function frame2():*
        {
            stop();
        }

        internal function frame3():*
        {
            stop();
        }


    }
}

