package
{
    import flash.display.MovieClip;

    public dynamic class firefoxTrail extends MovieClip
    {

        public function firefoxTrail()
        {
            super();
            addFrameScript(14, this.frame15);
        }

        internal function frame15():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

