package
{
    import flash.display.MovieClip;

    public dynamic class BM_Zz extends MovieClip
    {

        public function BM_Zz()
        {
            super();
            addFrameScript(27, this.frame28);
        }

        internal function frame28():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

