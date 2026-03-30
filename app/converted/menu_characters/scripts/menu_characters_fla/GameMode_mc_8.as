package menu_characters_fla
{
    import flash.display.MovieClip;

    public dynamic class GameMode_mc_8 extends MovieClip
    {

        public function GameMode_mc_8()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2);
        }

        internal function frame1():*
        {
            stop();
        }

        internal function frame2():*
        {
            stop();
        }


    }
}

