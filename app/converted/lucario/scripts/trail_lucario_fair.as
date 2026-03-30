package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_fair extends MovieClip
    {

        public function trail_lucario_fair()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

