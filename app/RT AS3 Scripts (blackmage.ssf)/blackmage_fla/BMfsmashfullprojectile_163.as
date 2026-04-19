// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.BMfsmashfullprojectile_163

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class BMfsmashfullprojectile_163 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var hitBox:MovieClip;
        internal var self:*;

        public function BMfsmashfullprojectile_163()
        {
            addFrameScript(0, this.frame1, 9, this.frame10, 39, this.frame40, 64, this.frame65, 75, this.frame76, 76, this.frame77);
        }

        public function toContinue(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
        }

        public function wallBounce(_arg_1:*):*
        {
            this.self.setXSpeed((this.self.getXSpeed() * -1));
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:*;
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
            };
        }

        internal function frame10():*
        {
            this.self.playSound("bmbolt");
            SSF2API.getCamera().shake(5);
        }

        internal function frame40():*
        {
            this.self.refreshAttackID();
        }

        internal function frame65():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame76():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame77():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}//package blackmage_fla

