package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Pitfall_103 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Pitfall_103()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }


    }
}

