package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemShoot_67 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemShoot_67()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

