package menu_characters_fla
{
    import flash.display.MovieClip;

    public dynamic class ReadyToFight_mc_113 extends MovieClip
    {

        public function ReadyToFight_mc_113()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.visible = false;
            this.mouseEnabled = false;
            this.mouseChildren = false;
            stop();
        }

        internal function frame11():*
        {
            gotoAndPlay("loop");
        }


    }
}

