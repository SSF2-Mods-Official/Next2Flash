package
{
    import flash.display.MovieClip;

    public dynamic class kirby_dkbar extends MovieClip
    {

        public function kirby_dkbar()
        {
            super();
            addFrameScript(9, this.frame10);
        }

        internal function frame10():*
        {
            gotoAndStop(1);
        }


    }
}

