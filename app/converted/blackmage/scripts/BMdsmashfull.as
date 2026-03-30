package
{
    import flash.display.MovieClip;

    public dynamic class BMdsmashfull extends MovieClip
    {

        public var stance:MovieClip;

        public function BMdsmashfull()
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

