package
{
    import flash.display.MovieClip;

    public dynamic class NSpecBomb2Dropped extends MovieClip
    {

        public var stance:MovieClip;

        public function NSpecBomb2Dropped()
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

