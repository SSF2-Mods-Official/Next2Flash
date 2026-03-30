package
{
    import flash.display.MovieClip;

    public dynamic class kirby_dice extends MovieClip
    {

        public var stance:MovieClip;

        public function kirby_dice()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            stop();
        }


    }
}

