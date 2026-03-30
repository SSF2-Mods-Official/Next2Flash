package
{
    import flash.display.MovieClip;

    public dynamic class NSpecBomb1Dropped extends MovieClip
    {

        public var stance:MovieClip;

        public function NSpecBomb1Dropped()
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

