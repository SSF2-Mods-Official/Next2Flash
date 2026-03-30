package menu_characters_fla
{
    import flash.display.MovieClip;

    public dynamic class HomeButton_3 extends MovieClip
    {

        public function HomeButton_3()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.buttonMode = true;
            this.mouseChildren = false;
            stop();
        }


    }
}

