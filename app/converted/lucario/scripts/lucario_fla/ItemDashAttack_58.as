package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemDashAttack_58 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemDashAttack_58()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 7, this.frame8, 14, this.frame15, 17, this.frame18, 20, this.frame21, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame6():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
        }

        internal function frame8():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame15():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame18():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame21():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

