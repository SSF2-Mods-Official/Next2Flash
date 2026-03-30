package
{
    import flash.display.MovieClip;

    public dynamic class foxTauntEffect extends MovieClip
    {

        public function foxTauntEffect()
        {
            super();
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

