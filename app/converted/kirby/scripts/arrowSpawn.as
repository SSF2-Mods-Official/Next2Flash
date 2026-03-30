package
{
    import flash.display.MovieClip;

    public dynamic class arrowSpawn extends MovieClip
    {

        public function arrowSpawn()
        {
            super();
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

