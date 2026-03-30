package
{
    import flash.display.MovieClip;

    public dynamic class aura_sphere extends MovieClip
    {

        public var stance:MovieClip;

        public function aura_sphere()
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

