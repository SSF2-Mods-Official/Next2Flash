package
{
    import flash.display.MovieClip;

    public dynamic class landboom extends MovieClip
    {

        public function landboom()
        {
            super();
            addFrameScript(22, this.frame23);
        }

        internal function frame23():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

