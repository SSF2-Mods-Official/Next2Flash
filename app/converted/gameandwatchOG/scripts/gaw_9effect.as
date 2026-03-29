package
{
    import flash.display.MovieClip;

    public dynamic class gaw_9effect extends MovieClip
    {

        public function gaw_9effect()
        {
            super();
            addFrameScript(19, this.frame20);
        }

        internal function frame20():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

