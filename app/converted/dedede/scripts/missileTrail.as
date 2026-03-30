package
{
    import flash.display.MovieClip;

    public dynamic class missileTrail extends MovieClip
    {

        public function missileTrail()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

