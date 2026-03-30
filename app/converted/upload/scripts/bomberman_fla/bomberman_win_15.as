package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_win_15 extends MovieClip
    {

        public function bomberman_win_15()
        {
            super();
            addFrameScript(78, this.frame79);
        }

        internal function frame79():*
        {
            gotoAndPlay("again");
        }


    }
}

