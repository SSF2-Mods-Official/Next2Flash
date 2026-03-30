package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_ledge extends MovieClip
    {

        public function trail_lucario_ledge()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

