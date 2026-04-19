// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ThiefProjectile_183

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class ThiefProjectile_183 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var self:*;
        public var jumpedToSwing:Boolean;
        public var oldX:Number;
        public var stuckCount:Number;
        public var character:*;
        public var temp:*;

        public function ThiefProjectile_183()
        {
            addFrameScript(0, this.frame1, 10, this.frame11, 11, this.frame12, 28, this.frame29, 38, this.frame39, 45, this.frame46, 50, this.frame51);
        }

        public function jumpToSwing():*
        {
            if (!this.jumpedToSwing)
            {
                this.self.setXSpeed(0);
                this.self.setYSpeed(0);
                this.jumpedToSwing = true;
                this.self.stancePlayFrame("attack");
                this.self.destroyTimer(this.checkStuck);
                this.self.destroyTimer(this.checkActivation);
            };
        }

        public function onHit(_arg_1:*=null):*
        {
            if (((_arg_1.data.receiver.isDisposed()) || (!(_arg_1.data.receiver.getType() === "SSF2Character"))))
            {
                return;
            };
            _arg_1.data.receiver.grab(this.character.getUID(), true, false, true);
            this.temp = this.character.getGlobalVariable("fsTargets");
            this.temp.push(_arg_1.data.receiver);
            this.character.setGlobalVariable("fsTargets", this.temp);
            SSF2API.getCamera().shake(10);
            this.jumpToSwing();
        }

        public function checkActivation():*
        {
            this.temp = this.character.getGlobalVariable("fsTargets");
            if (this.temp.length > 0)
            {
                this.jumpToSwing();
            };
        }

        public function checkStuck():*
        {
            if (this.oldX === this.self.getX())
            {
                this.stuckCount++;
                if (this.stuckCount > 5)
                {
                    this.jumpToSwing();
                };
            }
            else
            {
                this.stuckCount = 0;
            };
            this.oldX = this.self.getX();
        }

        public function land(_arg_1:*=null):*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.attachEffect("effect_land");
            this.self.stancePlayFrame("land");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.land);
            this.self.destroyTimer(this.checkStuck);
            this.self.destroyTimer(this.checkActivation);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.jumpedToSwing = false;
            this.oldX = 0;
            this.stuckCount = 0;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.onHit);
                this.self.createTimer(1, 0, this.checkActivation);
            };
        }

        internal function frame11():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame12():*
        {
            this.self.setXSpeed(28, false);
            this.self.setYSpeed(-20);
            this.self.updateProjectileStats({
                "gravity":1.5,
                "maxgravity":12
            });
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
            this.self.createTimer(1, 0, this.checkStuck);
        }

        internal function frame29():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame39():*
        {
            this.self.stancePlayFrame("endLoop");
        }

        internal function frame46():*
        {
            this.self.attachEffect("bm_fs_warp");
            this.self.playSound("bm_Warp_part2");
        }

        internal function frame51():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

