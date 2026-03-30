package
{
    import flash.display.MovieClip;

    public dynamic class dee_spear extends MovieClip
    {

        public var stance:b;

        public function dee_spear()
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

