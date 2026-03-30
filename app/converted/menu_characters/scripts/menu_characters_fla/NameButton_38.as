package menu_characters_fla
{
    import flash.display.MovieClip;

    public dynamic class NameButton_38 extends MovieClip
    {

        public function NameButton_38()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3);
        }

        internal function frame1():*
        {
            stop();
            this.buttonMode = true;
            this.mouseChildren = false;
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

