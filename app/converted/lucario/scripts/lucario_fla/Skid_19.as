package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_19 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Skid_19()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.playSound("lucario_skid");
                this.self.updateAuraPaws();
            };
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }


    }
}

