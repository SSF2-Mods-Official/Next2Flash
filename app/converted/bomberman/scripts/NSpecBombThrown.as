package
{
    import flash.display.MovieClip;

    public dynamic class NSpecBombThrown extends MovieClip
    {

        public var stance:MovieClip;

        public function NSpecBombThrown()
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

