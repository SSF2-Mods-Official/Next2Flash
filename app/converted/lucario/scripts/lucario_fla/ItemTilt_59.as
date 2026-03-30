package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemTilt_59 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemTilt_59()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 12, this.frame13, 14, this.frame15, 16, this.frame17, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame7():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame9():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame13():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame15():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame17():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

