package
{
    import flash.display.MovieClip;

    public dynamic class dthrow_bubbles extends MovieClip
    {

        public function dthrow_bubbles()
        {
            super();
            addFrameScript(39, this.frame40);
        }

        internal function frame40():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

