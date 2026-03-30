package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class kirby_star_168 extends MovieClip
    {

        public var attackBox:MovieClip;

        public function kirby_star_168()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            this.gotoAndStop("shoot");
        }


    }
}

