package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_23 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Helpless_23()
        {
            super();
            addFrameScript(0, this.frame1, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
                this.self.stancePlayFrame("again");
            };
        }

        internal function frame14():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

